import pandas as pd
import heapq
import json
from collections import deque

# ==============================
# LOAD DATA
# ==============================
# Load business rules configuration
with open("rules_config.json", "r") as f:
    config = json.load(f)

p_rules = config["passenger_priorities"]
f_rules = config["flight_ranking_rules"]
c_rules = config["constraints"]

flights = pd.read_csv("data/raw/flights.csv")
passengers = pd.read_csv("data/raw/passengers.csv")
pnr = pd.read_csv("data/raw/pnr_bookings.csv")
schedule_changes = pd.read_csv("data/raw/schedule_changes.csv")
schedule = pd.read_csv("data/raw/schedules.csv")
seats = pd.read_csv("data/raw/seat_inventory.csv")

# ==============================
# PREPROCESS
# ==============================

schedule['departure_time'] = pd.to_datetime(schedule['departure_time'])
schedule['arrival_time'] = pd.to_datetime(schedule['arrival_time'])

flights = flights.merge(schedule, on='flight_id', how='left')
flights = flights.merge(seats, on='flight_id', how='left')

# SINGLE SOURCE OF TRUTH FOR SEATS
seat_left = dict(zip(flights['flight_id'], flights['available_seats']))

# ==============================
# IMPACTED PASSENGERS
# ==============================

impacted_flights = schedule_changes['flight_id'].unique()
impacted_pnr = pnr[pnr['flight_id'].isin(impacted_flights)]

impacted = impacted_pnr.merge(passengers, on='passenger_id')
impacted = impacted.merge(flights, on='flight_id')

# ==============================
# PASSENGER PRIORITY
# ==============================

def passenger_priority(row):
    score = 0
    
    # 1. Base Class Score from Config
    if row['seat_class'] == 'FIRST':
        score += p_rules["FIRST_CLASS_SCORE"]
    elif row['seat_class'] == 'BUSINESS':
        score += p_rules["BUSINESS_CLASS_SCORE"]
    else:
        score += p_rules["ECONOMY_CLASS_SCORE"]
    
    # 2. Add Loyalty Level directly
    try:
        score += int(row['loyalty_level'])
    except:
        pass
        
    # 3. Apply New Mandatory Priority Markers
    if bool(row.get('is_unaccompanied_minor', False)):
        score += p_rules["UNACCOMPANIED_MINOR_SCORE"]
    if bool(row.get('is_on_duty_employee', False)):
        score += p_rules["ON_DUTY_EMPLOYEE_SCORE"]
        
    return score

impacted['priority'] = impacted.apply(passenger_priority, axis=1)

# ==============================
# BUILD HEAP
# ==============================

heap = []
TOP_K = 5

for i, row in impacted.iterrows():
    possible = flights[
        (flights['source_airport'] == row['source_airport']) &
        (flights['destination_airport'] == row['destination_airport']) &
        (flights['departure_time'] >= row['departure_time']) &
        (flights['flight_id'] != row['flight_id'])
    ].copy()

    if possible.empty:
        continue

    possible['delay'] = (possible['departure_time'] - row['departure_time']).dt.total_seconds()
    possible = possible.sort_values(by='delay').head(TOP_K)

    for _, f in possible.iterrows():
        score = (
            row['priority'] * 100
            - (f['delay'] * f_rules["DELAY_PENALTY_FACTOR"] / 60.0) # Penalty per minute of delay
            + seat_left[f['flight_id']] * f_rules["SEAT_AVAILABILITY_WEIGHT"]
            - (row['ancillary_fee_paid'] * f_rules["ANCILLARY_LOSS_PENALTY_FACTOR"])
        )
        heapq.heappush(heap, (-score, i, f['flight_id']))

# ==============================
# DIRECT MATCHING
# ==============================

assigned_passengers = set()
assignments = []

while heap:
    neg_score, p_idx, flight_id = heapq.heappop(heap)

    if p_idx in assigned_passengers:
        continue

    if seat_left[flight_id] <= 0:
        continue

    assigned_passengers.add(p_idx)
    seat_left[flight_id] -= 1

    row = impacted.loc[p_idx]

    delay = flights.loc[
        flights['flight_id'] == flight_id, 'departure_time'
    ].values[0] - row['departure_time']

    assignments.append({
        'pnr_id': row['pnr_id'],
        'passenger_id': row['passenger_id'],
        'old_flight': row['flight_id'],
        'new_flight': flight_id,
        'type': 'direct',
        'reason': f"Direct | Priority={row['priority']} | Delay={delay}"
    })

# ==============================
# BUILD GRAPH
# ==============================

graph = {}

for _, f in flights.iterrows():
    src = f['source_airport']
    if src not in graph:
        graph[src] = []
    graph[src].append(f)

# ==============================
# MULTI-HOP BFS
# ==============================

def find_multi_hop(row, max_stops=2):
    if not c_rules["ALLOW_MULTIHOP_FOR_MINORS"] and bool(row.get('is_unaccompanied_minor', False)):
        return None
    start = row['source_airport']
    end = row['destination_airport']
    start_time = row['departure_time']

    queue = deque()
    queue.append((start, start_time, [], 0))

    while queue:
        airport, curr_time, path, stops = queue.popleft()

        if stops > max_stops:
            continue

        if airport not in graph:
            continue

        for f in graph[airport]:
            if seat_left[f['flight_id']] <= 0:
                continue

            if f['departure_time'] < curr_time + pd.Timedelta(minutes=30):
                continue

            new_path = path + [f]

            if f['destination_airport'] == end:
                return new_path

            queue.append((
                f['destination_airport'],
                f['arrival_time'],
                new_path,
                stops + 1
            ))

    return None

# ==============================
# MULTI-HOP ASSIGNMENT
# ==============================

assigned_pnr = set([a['pnr_id'] for a in assignments])

for _, row in impacted.iterrows():
    if row['pnr_id'] in assigned_pnr:
        continue

    path = find_multi_hop(row)

    if path:
        valid = True
        for f in path:
            if seat_left[f['flight_id']] <= 0:
                valid = False
                break

        if not valid:
            continue

        for f in path:
            seat_left[f['flight_id']] -= 1

        route = " -> ".join([str(f['flight_id']) for f in path])

        assignments.append({
            'pnr_id': row['pnr_id'],
            'passenger_id': row['passenger_id'],
            'old_flight': row['flight_id'],
            'new_flight': route,
            'type': 'multi_hop',
            'reason': f"Multi-hop | Stops={len(path)-1}"
        })

# ==============================
# EXCEPTIONS
# ==============================

assigned_pnr = set([a['pnr_id'] for a in assignments])

exceptions = []

for _, row in impacted.iterrows():
    if row['pnr_id'] not in assigned_pnr:
        exceptions.append(row)

# ==============================
# SAVE OUTPUT
# ==============================

pd.DataFrame(assignments).to_csv(
    "data/processed/final_assignments_advanced.csv",
    index=False
)

pd.DataFrame(exceptions).to_csv(
    "data/processed/exceptions_advanced.csv",
    index=False
)

# ==============================
# STATS
# ==============================

total = len(impacted)
assigned_count = len(assignments)
unassigned_count = len(exceptions)

print("\n🔥 FINAL RESULTS (ADVANCED VERSION):")
print("Total impacted:", total)
print("Assigned:", assigned_count)
print("Unassigned:", unassigned_count)
print("Success Rate:", round(assigned_count / total * 100, 2), "%")

# ==============================
# METRICS
# ==============================

direct_count = sum(1 for a in assignments if a['type'] == 'direct')
multi_count = sum(1 for a in assignments if a['type'] == 'multi_hop')

print("\n📊 SYSTEM METRICS:")
print("Direct Assignments:", direct_count)
print("Multi-hop Assignments:", multi_count)
print("Multi-hop %:", round(multi_count / assigned_count * 100, 2), "%")
print("Unassigned %:", round(unassigned_count / total * 100, 2), "%")