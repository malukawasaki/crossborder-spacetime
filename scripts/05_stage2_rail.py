"""Stage 2 tables: weekday AM-peak rail dispersal from the gateway stations, by sector."""
import pandas as pd

from crossborder import config, io, stage2

print("Loading train OD ...")
train_od = io.load("origin_destination_train")

disp = stage2.am_dispersal(train_od)
io.write_table(stage2.gateway_sector_matrix(disp), "stage2_gateway_sector")
io.write_table(stage2.top_destinations(disp), "stage2_top10_per_gateway")

# Sensitivity: alternative AM windows give (nearly) the same sector shares.
rows = []
for label, hours in [("06:00-09:59", config.AM_PEAK_HOURS), ("06:00-08:59", config.AM_PEAK_SENSITIVITY_HOURS)]:
    d = stage2.am_dispersal(train_od, hours)
    s = d.groupby("sector").TOTAL_TRIPS.sum().reindex(stage2.SECTORS, fill_value=0)
    for sector, v in s.items():
        rows.append({"window": label, "sector": sector, "trips": int(v), "share_pct": 100 * v / s.sum()})
io.write_table(pd.DataFrame(rows), "stage2_sensitivity_window")
