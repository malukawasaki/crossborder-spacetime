"""Stage 1: Causeway bus crossings and the first (feeder) bus leg from Woodlands Checkpoint."""
import pandas as pd

from . import config
from .stations import bus_stop_name


def destination_group(code: str) -> str:
    for name, g in config.GATEWAYS.items():
        if code in g["bus_stops"]:
            return name
    if code in config.INDUSTRIAL_STOPS:
        return "Industrial stops"
    return "Other"


def crossings(bus_od: pd.DataFrame) -> pd.DataFrame:
    """Bus trips across the Causeway in each direction (bus OD), all days and weekdays."""
    pairs = {
        "JB -> SG": (config.JB_CP_TO_SG, config.WDL_CP_FROM_JB),
        "SG -> JB": (config.WDL_CP_TO_JB, config.JB_CP_FROM_SG),
    }
    rows = []
    for direction, (o, d) in pairs.items():
        x = bus_od[(bus_od.ORIGIN_PT_CODE == o) & (bus_od.DESTINATION_PT_CODE == d)]
        for day, sub in [("ALL", x), (config.WEEKDAY, x[x.DAY_TYPE == config.WEEKDAY])]:
            t = int(sub.TOTAL_TRIPS.sum())
            rows.append({"direction": direction, "origin": o, "destination": d, "day_type": day,
                         "trips": t, "trips_per_month": t / config.N_MONTHS})
    return pd.DataFrame(rows)


def onward_from_checkpoint(bus_od: pd.DataFrame) -> pd.DataFrame:
    """Trips boarding at 46109 (arrivals from JB) to Singapore stops, i.e. excluding checkpoint stops."""
    return bus_od[(bus_od.ORIGIN_PT_CODE == config.WDL_CP_FROM_JB)
                  & ~bus_od.DESTINATION_PT_CODE.isin(config.CHECKPOINT_STOPS)]


def feeder_split(bus_od: pd.DataFrame) -> pd.DataFrame:
    """Share of onward trips from 46109 by destination group (all days and weekdays)."""
    x = onward_from_checkpoint(bus_od)
    rows = []
    for day, sub in [("ALL", x), (config.WEEKDAY, x[x.DAY_TYPE == config.WEEKDAY])]:
        total = sub.TOTAL_TRIPS.sum()
        g = sub.groupby(sub.DESTINATION_PT_CODE.map(destination_group)).TOTAL_TRIPS.sum()
        for group in list(config.GATEWAYS) + ["Industrial stops", "Other"]:
            v = int(g.get(group, 0))
            rows.append({"day_type": day, "destination_group": group, "trips": v,
                         "trips_per_month": v / config.N_MONTHS, "share_pct": 100 * v / total})
        rows.append({"day_type": day, "destination_group": "Total", "trips": int(total),
                     "trips_per_month": total / config.N_MONTHS, "share_pct": 100.0})
    return pd.DataFrame(rows)


def top_destinations(bus_od: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    x = onward_from_checkpoint(bus_od)
    g = x.groupby("DESTINATION_PT_CODE").TOTAL_TRIPS.sum().sort_values(ascending=False)
    out = g.head(n).rename("trips").reset_index().rename(columns={"DESTINATION_PT_CODE": "stop_code"})
    out["stop_name"] = out.stop_code.map(bus_stop_name)
    out["group"] = out.stop_code.map(destination_group)
    out["share_pct"] = 100 * out.trips / g.sum()
    return out


def industrial_clusters(bus_od: pd.DataFrame) -> pd.DataFrame:
    """Onward trips from 46109 to each industrial-stop cluster: all days and weekday AM peak."""
    x = onward_from_checkpoint(bus_od)
    total = x.TOTAL_TRIPS.sum()
    am = x[(x.DAY_TYPE == config.WEEKDAY) & x.TIME_PER_HOUR.isin(config.AM_PEAK_HOURS)]
    rows = []
    for cluster, stops in config.INDUSTRIAL_CLUSTERS.items():
        v = int(x[x.DESTINATION_PT_CODE.isin(stops)].TOTAL_TRIPS.sum())
        rows.append({"cluster": cluster, "stops": " ".join(stops), "trips": v,
                     "trips_per_month": v / config.N_MONTHS, "share_of_onward_pct": 100 * v / total,
                     "weekday_am_peak_trips": int(am[am.DESTINATION_PT_CODE.isin(stops)].TOTAL_TRIPS.sum())})
    return pd.DataFrame(rows)


def corridor_stops(bus_node: pd.DataFrame, bus_od: pd.DataFrame) -> pd.DataFrame:
    """Tap-outs at the 20 corridor stops and how many of them are trips from a checkpoint stop."""
    tap = bus_node[bus_node.PT_CODE.isin(config.CORRIDOR_STOPS)].groupby("PT_CODE").TOTAL_TAP_OUT_VOLUME.sum()
    xb = bus_od[bus_od.ORIGIN_PT_CODE.isin(config.CHECKPOINT_STOPS)
                & bus_od.DESTINATION_PT_CODE.isin(config.CORRIDOR_STOPS)]
    xb = xb.groupby("DESTINATION_PT_CODE").TOTAL_TRIPS.sum()
    out = pd.DataFrame({"stop_code": config.CORRIDOR_STOPS})
    out["stop_name"] = out.stop_code.map(bus_stop_name)
    out["group"] = out.stop_code.map(
        lambda c: "JB Checkpoint" if c in (config.JB_CP_FROM_SG, config.JB_CP_TO_SG) else destination_group(c))
    out["tap_outs"] = out.stop_code.map(tap).fillna(0).astype(int)
    out["from_checkpoint_trips"] = out.stop_code.map(xb).fillna(0).astype(int)
    return out
