 

<!-- ```markdown -->
# Horizon Airways Flight Operations Center: Passenger Re-Accommodation Engine

An automated, high-throughput disruption management system that dynamically re-routes passengers during widespread flight delays and cancellations. Built with Python and Streamlit, this enterprise-grade operations terminal leverages a multi-criteria prioritization matrix and constrained graph traversal algorithms to process complex airline datasets containing **100K passengers** and **10K flights**.

---

## Technical Architecture Overview

The system is engineered around a localized search space optimization strategy, balancing strict operational safety constraints against airline profitability and customer retention indices.

### 1. Multi-Attribute Priority Matrix (Max-Heap)
Instead of a simple greedy sort, the core optimization loop structures affected passengers into a high-performance **Max-Heap array**. Priority coefficients are computed dynamically by pulling from an agent-configured rules schema:
- **Base Cabin Tiering:** Graded weights applied to First, Business, and Economy bookings.
- **Loyalty Program Metrics:** Scaled increments reflecting customer loyalty status levels.
- **Operational Safeguard Flags:** Significant priority boosts injected for **On-Duty Crew Members** and **Unaccompanied Minors (UMNR)** to ensure critical records are evaluated first.

### 2. Constrained Path Graph Traversal (Multi-Hop BFS)
When direct alternative flights are structurally exhausted, the engine instantiates an unweighted **Breadth-First Search (BFS)** across an airport adjacency graph up to a maximum depth of 2 stops:
- **Temporal Windows:** Enforces minimum 30-minute legal connection buffers between legs.
- **Vulnerable Passenger Safety Filters:** Programmatically isolates and blocks Unaccompanied Minors from being split onto multi-hop routes if restricted by active profile parameters.

### 3. Ancillary Preservation & Tier Grading
- **Financial Friction Metrics:** Penalizes flight alternatives that disrupt high-value, pre-paid ancillary services (e.g., baggage parameters, pre-booked meals, lounge clearances).
- **Seat Class Allocation Tracking:** Dynamically registers and logs automated cabin **Upgrades and Downgrades** when original flight tiers are at capacity.

<!-- --- -->

## Core System Performance

During baseline operational testing under a 2% schedule disruption factor across the network, the engine achieved the following benchmarks:

- **Total Disrupted Records Processed:** 2,017 Passengers
- **Successfully Accommodated:** 1,931 Passengers
- **Engine Accomplishment Index:** 95.74% Success Rate
  - **Direct Alternative Routings:** 1,494 Passengers
  - **Multi-Hop Connection Paths:** 437 Passengers
- **Isolated Exception Roster:** 86 Outliers (Automated separation of complex edge cases requiring manual desk intervention)

<!-- --- -->
<!--  -->
## User Interface & Control Panel

The system features a customized, dark-mode airport operations terminal interface built entirely without emojis for a clean, sleek corporate aesthetic. 

### Interactive Terminal Panel
*(Insert your Sidebar Control Panel Image Here)*

### Network Routing Analytics Dashboard
*(Insert your Main KPI Metrics Layout Image Here)*

### Passenger Manifest & Verification Logs
*(Insert your Data Tables and Tab Views Image Here)*

<!-- --- -->

## File Structure & Module Dependencies

```text
airline-reaccommodation-system/
├── data/
│   ├── raw/             # Input Tables (airports, flights, schedules, bookings)
│   └── processed/       # Manifest Outputs (final_assignments_advanced, exceptions)
├── rules_config.json    # Business Rule Engine JSON Schema Profiles
├── generate_dataset.py  # Synthetic Airline Schema Data Generator
├── reaccommodation.py  # Core Priority Heap & Graph Traversal Optimization Engine
├── app.py               # Enterprise Airport Operations Terminal UI (Streamlit)
└── requirements.txt     # Dependency Definitions

```

<!-- --- -->

## Installation & Local Deployment

### 1. Initialize Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate

```

### 2. Install Project Dependencies

```bash
pip install streamlit pandas numpy --default-timeout=100 --no-cache-dir

```

### 3. Generate Core Relational Data Tables

```bash
python generate_dataset.py

```

### 4. Boot Up the Flight Operations Dashboard

```bash
.\venv\Scripts\python.exe -m streamlit run app.py

```

```

 
```