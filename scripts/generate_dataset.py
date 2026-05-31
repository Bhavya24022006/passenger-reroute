import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

NUM_AIRPORTS = 50
NUM_FLIGHTS = 10000
NUM_PASSENGERS = 100000
SCHEDULE_CHANGE_RATIO = 0.02

# Ensure data directory exists
os.makedirs("data/raw", exist_ok=True)

# -----------------------
# Airports
# -----------------------
airports = pd.DataFrame({
    "airport_code": [f"AP{i:03d}" for i in range(NUM_AIRPORTS)],
    "city": [f"City_{i}" for i in range(NUM_AIRPORTS)],
    "country": ["Country_X"] * NUM_AIRPORTS
})

# -----------------------
# Flights
# -----------------------
codes = airports["airport_code"].tolist()

flights = []
for i in range(NUM_FLIGHTS):
    src, dst = random.sample(codes, 2)
    flights.append({
        "flight_id": f"FL{i:05d}",
        "airline": "AI",
        "source_airport": src,
        "destination_airport": dst
    })

flights = pd.DataFrame(flights)

# -----------------------
# Flight schedules
# -----------------------
start = datetime(2026, 1, 1)

schedules = []
for fid in flights["flight_id"]:
    dep = start + timedelta(minutes=random.randint(0, 60*24*30))
    arr = dep + timedelta(minutes=random.randint(60, 600))
    schedules.append({
        "flight_id": fid,
        "departure_time": dep,
        "arrival_time": arr
    })

schedules = pd.DataFrame(schedules)

# -----------------------
# Seat inventory
# -----------------------
inventory = pd.DataFrame({
    "flight_id": flights["flight_id"],
    "total_seats": np.random.randint(120, 220, size=NUM_FLIGHTS)
})

inventory["available_seats"] = inventory["total_seats"]

# -----------------------
# Passengers
# -----------------------
ptype = ["NORMAL", "LOYALTY", "VIP", "UNACCOMPANIED_MINOR"]

passengers = pd.DataFrame({
    "passenger_id": [f"P{i:06d}" for i in range(NUM_PASSENGERS)],
    "name": [f"Passenger_{i}" for i in range(NUM_PASSENGERS)],
    "passenger_type": np.random.choice(ptype, NUM_PASSENGERS),
    "loyalty_level": np.random.randint(0, 5, size=NUM_PASSENGERS),
    "is_unaccompanied_minor": np.random.choice([True, False], NUM_PASSENGERS, p=[0.02, 0.98]),
    "is_on_duty_employee": np.random.choice([True, False], NUM_PASSENGERS, p=[0.03, 0.97])
})

# -----------------------
# PNR bookings
# -----------------------
pnr = pd.DataFrame({
    "pnr_id": [f"PNR{i:06d}" for i in range(NUM_PASSENGERS)],
    "passenger_id": passengers["passenger_id"],
    "flight_id": np.random.choice(flights["flight_id"], NUM_PASSENGERS),
    "seat_class": np.random.choice(["ECONOMY", "BUSINESS", "FIRST"], NUM_PASSENGERS),
    "ancillary_fee_paid": np.random.randint(0, 150, size=NUM_PASSENGERS)
})

# -----------------------
# Schedule changes
# -----------------------
num_changes = int(NUM_FLIGHTS * SCHEDULE_CHANGE_RATIO)

changes = pd.DataFrame({
    "flight_id": np.random.choice(flights["flight_id"], num_changes, replace=False),
    "change_type": np.random.choice(["DELAY", "CANCELLED"], num_changes),
    "change_minutes": np.random.randint(30, 300, size=num_changes)
})

# -----------------------
# Save files
# -----------------------
airports.to_csv("data/raw/airports.csv", index=False)
flights.to_csv("data/raw/flights.csv", index=False)
schedules.to_csv("data/raw/schedules.csv", index=False)
inventory.to_csv("data/raw/seat_inventory.csv", index=False)
passengers.to_csv("data/raw/passengers.csv", index=False)
pnr.to_csv("data/raw/pnr_bookings.csv", index=False)
changes.to_csv("data/raw/schedule_changes.csv", index=False)

print("Dataset generated successfully in data/raw/")