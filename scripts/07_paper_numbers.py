"""Collect every quantitative claim of Section 4.1 and compare it with the recomputed value.

Reads only the committed tables in results/tables and writes results/tables/paper_numbers.csv.
Status: "match" = same number, "changed" = number differs, "reinterpreted" = number reproduces
but describes something different from what the original text says.
"""
import pandas as pd

from crossborder import config, io, spacetime

P = f"{config.PERIOD[0]}..{config.PERIOD[-1]}"
N = config.N_MONTHS

cross = io.read_table("stage1_causeway_crossings").set_index(["direction", "day_type"])
split = io.read_table("stage1_feeder_split_46109").set_index(["day_type", "destination_group"])
ind = io.read_table("stage1_industrial_clusters")
corr = io.read_table("stage1_corridor_stops")
hourly = io.read_table("rhythms_checkpoint_hourly").query("day_type == 'WEEKDAY'").set_index("hour")
sect = io.read_table("stage2_gateway_sector").set_index(["gateway", "sector"])
sens = io.read_table("stage2_sensitivity_window").set_index(["window", "sector"])

rows = []


def claim(text, paper, value, unit, script, status, note=""):
    rows.append({"claim": text, "paper_value": paper, "recomputed_value": value, "unit": unit, "period": P,
                 "script": script, "status": status, "note": note})


S1, S2, RH = "scripts/03_stage1_bus.py", "scripts/05_stage2_rail.py", "scripts/04_rhythms.py"

# ---- Corridor volume
corr_total = int(corr.tap_outs.sum())
corr_xb = int(corr.from_checkpoint_trips.sum())
claim("Bus tap-outs at the 20 corridor stops (10-month total)", 32251201, corr_total, "tap-outs", S1, "changed",
      "Stop list now uses 47009 (Woodlands Temp Int) instead of 46009 (Woodlands Int), which receives no "
      f"checkpoint trips. {corr_xb:,} ({100 * corr_xb / corr_total:.1f}%) of these tap-outs are trips that "
      "started at a checkpoint stop; the rest is local Singapore traffic.")
claim("Bus tap-outs at the 20 corridor stops (monthly mean)", 3225120, round(corr_total / N), "tap-outs/month",
      S1, "changed", "See previous row.")
for d, label in [("JB -> SG", "46219 -> 46109"), ("SG -> JB", "46101 -> 46211")]:
    claim(f"Causeway bus crossings {d} ({label}), all days, 10-month total", "", int(cross.loc[(d, "ALL"), "trips"]),
          "trips", S1, "new", "Recommended headline volume for the Causeway bus corridor.")

# ---- Stage 1 feeder split from 46109
for grp, paper in [("Kranji", 55.83), ("Woodlands", 17.08), ("Marsiling", 14.76)]:
    claim(f"Share of onward bus trips from Woodlands Checkpoint (46109) to {grp}", paper,
          round(split.loc[("ALL", grp), "share_pct"], 2), "%", S1, "changed",
          "Original value used Jun-Dec 2025 only (7 months). Weekday: "
          f"{split.loc[('WEEKDAY', grp), 'share_pct']:.2f}%.")
three = sum(split.loc[("ALL", g), "share_pct"] for g in config.GATEWAYS)
three_trips = sum(split.loc[("ALL", g), "trips"] for g in config.GATEWAYS)
claim("Share of onward trips ending at the three gateways", 87.67, round(three, 2), "%", S1, "changed", "")
claim("Onward trips to the three gateways (monthly)", 2830000, round(three_trips / N), "trips/month", S1,
      "changed", "Original = 87.67% x 3.23M corridor tap-outs, mixing two different measures.")
claim("Kranji feeder trips (10-month total)", 17580000, int(split.loc[("ALL", "Kranji"), "trips"]), "trips", S1,
      "changed", "Original = 55.83% x 31.49M tap-outs; not a measured flow.")
ind_share = split.loc[("ALL", "Industrial stops"), "share_pct"]
claim("Share of onward trips to industrial-area stops", 6.82, round(ind_share, 2), "%", S1, "changed",
      "Original = industrial-stop tap-outs / corridor tap-outs (incl. Mar-May 2022). Two of the 13 stops are "
      "residential/retail (Marsiling Mall, Blk 347); Kranji Loop/Way and Admiralty Rd West stops receive no "
      "trips from the checkpoint.")
claim("Onward trips to industrial-area stops (monthly)", 220000, round(split.loc[("ALL", "Industrial stops"),
      "trips"] / N), "trips/month", S1, "changed", "")
claim("Weekday AM-peak (06:00-09:59) trips from the checkpoint to industrial-area stops (10-month total)", 412528,
      int(ind.weekday_am_peak_trips.sum()), "trips", S1, "changed",
      "Original counted all tap-outs at the stops, not trips from the checkpoint.")

# ---- Hourly rhythm at 46101 (Singapore -> JB stop)
REINT = ("Value reproduces, but 46101 serves Singapore -> JB travel: tap-outs are passengers arriving on local "
         "Singapore buses to leave for JB; tap-ins board buses to JB. JB -> SG arrivals are at 46109 (S1).")
for paper_label, h, paper in [("04:00-05:00", 5, 9417), ("05:00-06:00", 6, 60025), ("06:00-07:00", 7, 125556),
                              ("07:00-08:00", 8, 242101), ("09:00-10:00 (peak)", 10, 251467),
                              ("11:00", 11, 235333), ("13:00", 13, 181536)]:
    claim(f"Weekday tap-outs at 46101, paper label {paper_label}", paper,
          int(hourly.loc[h, "sg_to_jb_tap_out_46101"]), "tap-outs (10-month sum)", RH, "reinterpreted",
          f"Correct hour label: {hourly.loc[h, 'hour_label']}. " + REINT)
for paper_label, h, paper in [("07:00", 7, 129628), ("10:00-11:00 (peak)", 10, 297163)]:
    claim(f"Weekday tap-ins at 46101, paper label {paper_label}", paper,
          int(hourly.loc[h, "sg_to_jb_tap_in_46101"]), "tap-ins (10-month sum)", RH, "reinterpreted",
          f"Hour {hourly.loc[h, 'hour_label']}. " + REINT)
ratio = hourly.loc[7, "sg_to_jb_tap_in_46101"] / hourly.loc[7, "sg_to_jb_tap_out_46101"]
claim("Tap-in / tap-out ratio at 46101, 07:00-07:59", 1.03, round(ratio, 2), "ratio", RH, "reinterpreted",
      "Both flows are Singapore -> JB; the ratio says nothing about clearance of JB arrivals.")
dip = 100 * (1 - hourly.loc[13, "sg_to_jb_tap_out_46101"] / hourly.loc[11, "sg_to_jb_tap_out_46101"])
claim("Midday decline in 46101 tap-outs, 11:00 -> 13:00", 22.9, round(dip, 1), "%", RH, "reinterpreted", REINT)
peak_h = int(hourly.jb_to_sg_tap_in_46109.idxmax())
claim("Peak hour of JB -> SG boardings at 46109 (weekday)", "", hourly.loc[peak_h, "hour_label"], "hour", RH,
      "new", f"{int(hourly.jb_to_sg_tap_in_46109.max()):,} boardings; crossings 46219 -> 46109 peak at "
      f"{hourly.loc[int(hourly.jb_to_sg_crossings.idxmax()), 'hour_label']}.")

# ---- Stage 2
tot = int(sum(sect.loc[("Total", s), "trips"] for s in sect.loc["Total"].index))
claim("Weekday AM-peak (06:00-09:59) rail trips from the three gateways (10-month total)", 9245358, tot, "trips",
      S2, "changed", "Original included Mar-May 2022 (13 months) and was described as monthly. "
      "These are all passengers tapping in at the gateways, not only cross-border commuters.")
for sector, paper_pct, paper_trips in [("CBD & Civic Core", 19.76, 1826447), ("Secondary Gateways", 16.17, 1495273),
                                       ("Industrial West", 14.72, 1361294), ("Industrial East", 7.44, 687510),
                                       ("Northern & Central Heartlands", 22.78, 2105645),
                                       ("Other", 19.14, 1769189)]:
    claim(f"Stage 2 share: {sector}", paper_pct, round(sect.loc[("Total", sector), "share_of_gateway_pct"], 2), "%",
          S2, "changed", "")
    claim(f"Stage 2 trips: {sector}", paper_trips, int(sect.loc[("Total", sector), "trips"]), "trips", S2,
          "changed", "")
early = int(sum(sens.loc["06:00-08:59"].trips))
claim("Weekday rail trips from the gateways, 06:00-08:59", 8070000, early, "trips", S2, "changed",
      f"{100 * early / tot:.1f}% of the 06:00-09:59 total.")

# ---- Space-time profiles
prof = spacetime.load_profiles()
km = prof["corridor_km"]["Woodlands Checkpoint"] - prof["corridor_km"]["JB CIQ"]
lo, hi = spacetime.crossing_speed_kmh(km, 90), spacetime.crossing_speed_kmh(km, 60)
claim("Causeway crossing speed (1.06 km in 60-90 min)", "0.71-1.06", f"{lo:.2f}-{hi:.2f}", "km/h",
      "src/crossborder/spacetime.py", "match", "From interview-reported crossing times.")

out = pd.DataFrame(rows)
out["paper_value"] = out.paper_value.astype(str)
out["recomputed_value"] = out.recomputed_value.astype(str)
io.write_table(out, "paper_numbers")
print(out.status.value_counts().to_string())
