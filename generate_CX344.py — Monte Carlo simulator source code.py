"""
Focused Airline Overbooking Dataset — Single Flight, 3 Months
================================================================
Flight:    CX344  HKG → PEK  (Cathay Pacific)
Aircraft:  Airbus A330-300 (A333), 262 seats (39J + 223Y)
Period:    2024-06-01 to 2024-08-31 (summer peak, 92 days)
Currency:  HKD

Each row = one daily flight. This is your RAW DATA for the IA.
"""

import numpy as np
import pandas as pd
from datetime import date, timedelta

np.random.seed(2024)

# ============================================================
# Flight parameters
# ============================================================
FLIGHT_NUMBER = "CX344"
AIRLINE       = "Cathay Pacific"
ROUTE         = "HKG-PEK"
AIRCRAFT      = "Airbus A330-300"
AIRCRAFT_CODE = "A333"
CAPACITY      = 262          # seats (Cathay regional A330-300: 39J + 223Y)
BASE_FARE     = 2400         # HKD average one-way economy (summer)
COMPENSATION  = 5000         # HKD per bumped passenger (denied boarding comp + rebooking)
BASE_P        = 0.90         # base show-up probability

START = date(2024, 6, 1)
END   = date(2024, 8, 31)
NUM_DAYS = (END - START).days + 1

# ============================================================
# Generate one flight per day
# ============================================================
records = []

for i in range(NUM_DAYS):
    d = START + timedelta(days=i)
    dow = d.weekday()  # 0=Mon ... 6=Sun

    # --- Ticket price: base fare × weekend premium × random noise ---
    fare_mult = 1.18 if dow in (4, 5, 6) else 1.0   # Fri/Sat/Sun premium
    fare = BASE_FARE * fare_mult * np.random.normal(1.0, 0.06)
    fare = round(fare, 2)

    # --- Tickets sold: airline overbooks, busier on Thu/Fri/Sun ---
    demand_mult = 1.07 if dow in (3, 4, 6) else 1.02
    overbook_ratio = np.clip(
        np.random.normal(1.06 * demand_mult, 0.03),
        0.93,   # occasionally underbooked
        1.14    # max overbooking
    )
    tickets_sold = int(round(CAPACITY * overbook_ratio))

    # --- Show-up: Binomial(tickets_sold, p) with slight day-to-day variation ---
    p = np.clip(BASE_P + np.random.normal(0, 0.012), 0.85, 0.96)
    showed_up = np.random.binomial(n=tickets_sold, p=p)

    # --- Derived fields ---
    no_shows     = tickets_sold - showed_up
    bumped       = max(0, showed_up - CAPACITY)
    ticket_rev   = round(fare * tickets_sold, 2)
    comp_cost    = bumped * COMPENSATION
    net_rev      = round(ticket_rev - comp_cost, 2)

    records.append({
        "date":            d.isoformat(),
        "day_of_week":     d.strftime("%A"),
        "flight_number":   FLIGHT_NUMBER,
        "airline":         AIRLINE,
        "route":           ROUTE,
        "aircraft":        AIRCRAFT,
        "aircraft_code":   AIRCRAFT_CODE,
        "capacity":        CAPACITY,
        "tickets_sold":    tickets_sold,
        "showed_up":       showed_up,
        "no_shows":        no_shows,
        "bumped":          bumped,
        "avg_fare_hkd":    fare,
        "ticket_revenue_hkd":  ticket_rev,
        "compensation_hkd":    comp_cost,
        "net_revenue_hkd":     net_rev,
    })

# ============================================================
# Save & summarise
# ============================================================
df = pd.DataFrame(records)
df.to_csv("CX344_HKG-PEK_JunAug2024.csv", index=False)

print("=" * 65)
print(f"DATASET: {AIRLINE} {FLIGHT_NUMBER} ({ROUTE})")
print(f"Aircraft: {AIRCRAFT} ({AIRCRAFT_CODE}), {CAPACITY} seats")
print(f"Period: {START} → {END}")
print("=" * 65)
print(f"  Flights:              {len(df)}")
print(f"  Mean tickets sold:    {df['tickets_sold'].mean():.1f}")
print(f"  Mean showed up:       {df['showed_up'].mean():.1f}")
print(f"  Overall no-show rate: {df['no_shows'].sum()/df['tickets_sold'].sum():.2%}")
print(f"  Flights with bumps:   {(df['bumped']>0).sum()} ({(df['bumped']>0).mean():.1%})")
print(f"  Total bumped pax:     {df['bumped'].sum()}")
print(f"  Mean fare:            HKD {df['avg_fare_hkd'].mean():,.2f}")
print(f"  Mean net revenue:     HKD {df['net_revenue_hkd'].mean():,.2f}")
print()
print("First 5 rows:")
print(df.head().to_string(index=False))
print()
print(f"Saved: CX344_HKG-PEK_JunAug2024.csv ({len(df)} rows)")
