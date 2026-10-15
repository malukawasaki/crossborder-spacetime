"""Hourly rhythms at the Causeway, by direction of travel."""
import pandas as pd

from . import config


def checkpoint_hourly(bus_od: pd.DataFrame, bus_node: pd.DataFrame) -> pd.DataFrame:
    """10-month hourly totals per day type for both directions.

    JB -> SG: bus crossings 46219 -> 46109 and boardings (tap-ins) at 46109.
    SG -> JB: alightings (tap-outs) at 46101, boardings (tap-ins) at 46101 and crossings 46101 -> 46211.
    """
    def od_pair(o, d):
        x = bus_od[(bus_od.ORIGIN_PT_CODE == o) & (bus_od.DESTINATION_PT_CODE == d)]
        return x.groupby(["DAY_TYPE", "TIME_PER_HOUR"]).TOTAL_TRIPS.sum()

    def node(code, col):
        x = bus_node[bus_node.PT_CODE == code]
        return x.groupby(["DAY_TYPE", "TIME_PER_HOUR"])[col].sum()

    series = {
        "jb_to_sg_crossings": od_pair(config.JB_CP_TO_SG, config.WDL_CP_FROM_JB),
        "jb_to_sg_tap_in_46109": node(config.WDL_CP_FROM_JB, "TOTAL_TAP_IN_VOLUME"),
        "sg_to_jb_tap_out_46101": node(config.WDL_CP_TO_JB, "TOTAL_TAP_OUT_VOLUME"),
        "sg_to_jb_tap_in_46101": node(config.WDL_CP_TO_JB, "TOTAL_TAP_IN_VOLUME"),
        "sg_to_jb_crossings": od_pair(config.WDL_CP_TO_JB, config.JB_CP_FROM_SG),
    }
    idx = pd.MultiIndex.from_product([sorted(bus_node.DAY_TYPE.unique()), range(24)],
                                     names=["day_type", "hour"])
    out = pd.DataFrame({k: v.reindex(idx, fill_value=0) for k, v in series.items()}).astype(int)
    out = out.reset_index()
    out.insert(2, "hour_label", out.hour.map(lambda h: f"{h:02d}:00-{h:02d}:59"))
    return out


def industrial_hourly(bus_od: pd.DataFrame) -> pd.DataFrame:
    """Weekday hourly onward trips from 46109 to each industrial cluster."""
    x = bus_od[(bus_od.ORIGIN_PT_CODE == config.WDL_CP_FROM_JB) & (bus_od.DAY_TYPE == config.WEEKDAY)]
    cols = {}
    for cluster, stops in config.INDUSTRIAL_CLUSTERS.items():
        cols[cluster] = (x[x.DESTINATION_PT_CODE.isin(stops)].groupby("TIME_PER_HOUR").TOTAL_TRIPS.sum()
                         .reindex(range(24), fill_value=0))
    out = pd.DataFrame(cols).astype(int)
    out.index.name = "hour"
    return out.reset_index()
