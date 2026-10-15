"""Loaders for the LTA DataMall passenger-volume files.

Every loader keeps only the study period (config.PERIOD) and fails loudly if a month is
missing, so that no table can silently mix in other months.
"""
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from . import config

FAMILIES = {
    "transport_node_bus": "PT_CODE",
    "transport_node_train": "PT_CODE",
    "origin_destination_bus": "ORIGIN_PT_CODE",
    "origin_destination_train": "ORIGIN_PT_CODE",
}


def month_file(family: str, year_month: str, data_dir: Optional[Path] = None) -> Path:
    """Path of one monthly file, e.g. data/raw/lta/origin_destination_bus_202506.csv."""
    root = Path(data_dir or config.DATA_DIR) / "lta"
    return root / f"{family}_{year_month.replace('-', '')}.csv"


def period_files(family: str, data_dir: Optional[Path] = None) -> List[Path]:
    files = [month_file(family, ym, data_dir) for ym in config.PERIOD]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        raise FileNotFoundError(f"{family}: missing {len(missing)} file(s): {', '.join(missing)}")
    return files


def filter_period(df: pd.DataFrame, period: Iterable[str] = config.PERIOD) -> pd.DataFrame:
    """Keep rows inside the study period; raise if the data contain other months or miss some."""
    period = list(period)
    months = set(df["YEAR_MONTH"].astype(str))
    outside = sorted(months - set(period))
    if outside:
        raise ValueError(f"data contain months outside the study period: {outside}")
    absent = sorted(set(period) - months)
    if absent:
        raise ValueError(f"study period months absent from data: {absent}")
    return df


def _normalise_codes(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("PT_CODE", "ORIGIN_PT_CODE", "DESTINATION_PT_CODE"):
        if col in df and (df["PT_TYPE"] == "BUS").all():
            df[col] = df[col].astype(str).str.zfill(5)
    return df


def load(family: str, data_dir: Optional[Path] = None, origins: Optional[Iterable[str]] = None,
         destinations: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """Load one file family for the study period.

    ``origins`` / ``destinations`` restrict OD files while reading (the bus OD files are
    ~240 MB per month); a row is kept if it matches either filter.
    """
    code_cols = {"PT_CODE": str, "ORIGIN_PT_CODE": str, "DESTINATION_PT_CODE": str}
    parts = []
    for f in period_files(family, data_dir):
        for chunk in pd.read_csv(f, dtype=code_cols, chunksize=2_000_000):
            chunk = _normalise_codes(chunk)
            if origins is not None or destinations is not None:
                keep = pd.Series(False, index=chunk.index)
                if origins is not None:
                    keep |= chunk["ORIGIN_PT_CODE"].isin(set(origins))
                if destinations is not None:
                    keep |= chunk["DESTINATION_PT_CODE"].isin(set(destinations))
                chunk = chunk[keep]
            parts.append(chunk)
    return filter_period(pd.concat(parts, ignore_index=True))


def read_table(name: str) -> pd.DataFrame:
    return pd.read_csv(config.TABLES_DIR / f"{name}.csv", dtype={"stop_code": str, "code": str})


def write_table(df: pd.DataFrame, name: str) -> Path:
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.TABLES_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"  wrote {path.relative_to(config.REPO_ROOT)} ({len(df)} rows)")
    return path
