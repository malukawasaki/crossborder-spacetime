"""Stage 2: weekday AM-peak rail dispersal from the three gateway stations."""
from typing import Iterable

import pandas as pd

from . import config
from .stations import station_name

# Keyword lists as used in the manuscript; matched against lower-case station names.
SECTOR_KEYWORDS = {
    "CBD & Civic Core": [
        "city hall", "raffles", "tanjong pagar", "downtown", "marina", "shenton", "telok ayer", "orchard",
        "somerset", "dhoby", "novena", "newton", "bugis", "lavender", "bencoolen", "clarke quay",
        "chinatown", "rochor", "bras basah", "esplanade", "fort canning", "outram park", "havelock",
        "maxwell"],
    "Secondary Gateways": ["jurong east", "clementi", "choa chu kang", "bukit batok"],
    "Industrial West": [
        "boon lay", "pioneer", "joo koon", "gul", "tuas", "yew tee", "chinese garden", "lakeside", "dover",
        "buona vista", "one-north", "kent ridge", "haw par", "pasir panjang"],
    "Industrial East": [
        "tai seng", "macpherson", "ubi", "kaki bukit", "bedok north", "bedok reservoir", "tampines", "expo",
        "changi", "pasir ris", "simei", "tanah merah", "kembangan", "eunos", "aljunied", "paya lebar",
        "mattar", "geylang bahru", "bendemeer", "potong pasir", "woodleigh", "serangoon", "kovan",
        "hougang", "buangkok", "sengkang", "punggol", "bartley", "lorong chuan"],
    "Northern & Central Heartlands": [
        "yishun", "yio chu kang", "ang mo kio", "sembawang", "khatib", "toa payoh", "bishan", "braddell",
        "canberra", "lentor", "mayflower", "bright hill", "upper thomson", "caldecott"],
}
SECTORS = list(SECTOR_KEYWORDS) + ["Other"]


def classify_sector(name: str) -> str:
    """Macro functional sector of a station name (first matching sector wins)."""
    n = str(name).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(k in n for k in keywords):
            return sector
    return "Other"


def is_dispersal_destination(code: str) -> bool:
    return not any(part in config.NON_DISPERSAL_CODES for part in str(code).split("/"))


def am_dispersal(train_od: pd.DataFrame, hours: Iterable[int] = config.AM_PEAK_HOURS) -> pd.DataFrame:
    """Weekday trips from the gateway stations in the given hours, with destination name and sector."""
    x = train_od[(train_od.DAY_TYPE == config.WEEKDAY) & train_od.TIME_PER_HOUR.isin(list(hours))
                 & train_od.ORIGIN_PT_CODE.isin(config.GATEWAY_STATIONS)]
    x = x[x.DESTINATION_PT_CODE.map(is_dispersal_destination)].copy()
    x["gateway"] = x.ORIGIN_PT_CODE.map(config.GATEWAY_STATIONS)
    x["destination"] = x.DESTINATION_PT_CODE.map(station_name)
    x["sector"] = x.destination.map(classify_sector)
    return x


def gateway_sector_matrix(disp: pd.DataFrame) -> pd.DataFrame:
    m = disp.pivot_table(index="gateway", columns="sector", values="TOTAL_TRIPS", aggfunc="sum", fill_value=0)
    m = m.reindex(index=list(config.GATEWAYS), columns=SECTORS, fill_value=0)
    m.loc["Total"] = m.sum()
    long = m.reset_index().melt(id_vars="gateway", var_name="sector", value_name="trips")
    long["share_of_gateway_pct"] = 100 * long.trips / long.groupby("gateway").trips.transform("sum")
    long["trips_per_month"] = long.trips / config.N_MONTHS
    return long


def top_destinations(disp: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    g = disp.groupby(["gateway", "destination", "sector"]).TOTAL_TRIPS.sum().reset_index(name="trips")
    g["rank"] = g.groupby("gateway").trips.rank(ascending=False, method="first").astype(int)
    return g[g["rank"] <= n].sort_values(["gateway", "rank"]).reset_index(drop=True)
