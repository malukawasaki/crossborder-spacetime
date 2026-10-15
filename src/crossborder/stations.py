"""Code -> name / coordinate lookups for train stations and the bus stops used in the study."""
from functools import lru_cache
from typing import Optional, Tuple

import pandas as pd

from . import config


@lru_cache(maxsize=1)
def train_stations() -> pd.DataFrame:
    return pd.read_csv(config.REFERENCE_DIR / "train_stations.csv").set_index("code")


@lru_cache(maxsize=1)
def bus_stops() -> pd.DataFrame:
    return pd.read_csv(config.REFERENCE_DIR / "bus_stops.csv", dtype={"code": str}).set_index("code")


def station_name(code: str, table: Optional[pd.DataFrame] = None) -> str:
    """Name of a train station code; composite codes (e.g. 'NS9/TE2') resolve via any part.

    Unknown codes are returned unchanged.
    """
    table = train_stations() if table is None else table
    for candidate in [code] + str(code).split("/"):
        if candidate in table.index and pd.notna(table.at[candidate, "name"]):
            return table.at[candidate, "name"]
    return str(code)


def station_lonlat(name: str) -> Optional[Tuple[float, float]]:
    t = train_stations().dropna(subset=["lon"])
    hit = t[t["name"] == name]
    return None if hit.empty else (float(hit["lon"].iloc[0]), float(hit["lat"].iloc[0]))


def bus_stop_name(code: str) -> str:
    t = bus_stops()
    return t.at[code, "name"] if code in t.index else code


def cluster_lonlat(stop_codes) -> Tuple[float, float]:
    t = bus_stops().reindex(stop_codes).dropna(subset=["lon"])
    return float(t["lon"].mean()), float(t["lat"].mean())
