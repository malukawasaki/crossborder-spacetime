"""Rebuild data/reference/landuse_mp2019.geojson (simplified URA Master Plan 2019 land use)
and the station coordinates in data/reference/train_stations.csv from the raw inputs.

The outputs are committed, so this step is only needed to regenerate them.
"""
import geopandas as gpd
import pandas as pd

from crossborder import config

MP2019 = config.DATA_DIR / "ura" / "Masterplan2019PBremoved.shp"
EXITS = config.DATA_DIR / "lta" / "LTAMRTStationExitGEOJSON.geojson"
INFRASTRUCTURE = {"ROAD", "MASS RAPID TRANSIT", "LIGHT RAPID TRANSIT", "TRANSPORT FACILITIES",
                  "WATERBODY", "RESERVE SITE"}


def landuse_category(desc: str):
    d = str(desc).upper()
    if any(k in d for k in ("COMMERCIAL", "WHITE", "HOTEL")):
        return "Commercial"
    if any(k in d for k in ("BUSINESS 1", "BUSINESS 2", "BUSINESS PARK")):
        return "Industrial / Business"
    if "RESIDENTIAL" in d:
        return "Residential"
    if any(k in d for k in ("PARK", "OPEN SPACE", "RECREATION")):
        return "Parks & Open Space"
    if any(k in d for k in ("HEALTH", "MEDICAL", "CIVIC", "EDUCATIONAL", "INSTITUTION", "WORSHIP")):
        return "Civic & Institutional"
    return None


def build_landuse() -> None:
    mp = gpd.read_file(MP2019).to_crs(3414)
    mp = mp[~mp["lu_desc"].isin(INFRASTRUCTURE)].copy()
    mp["category"] = mp["lu_desc"].map(landuse_category)
    mp = mp.dropna(subset=["category"])
    mp["geometry"] = mp.buffer(0)
    lu = mp[["category", "geometry"]].dissolve(by="category").reset_index()
    lu["geometry"] = lu.simplify(25, preserve_topology=True)
    out = config.REFERENCE_DIR / "landuse_mp2019.geojson"
    lu.to_crs(4326).to_file(out, driver="GeoJSON", COORDINATE_PRECISION=5)
    print(f"  wrote {out.relative_to(config.REPO_ROOT)} ({out.stat().st_size / 1e6:.1f} MB)")


def refresh_station_coords() -> None:
    path = config.REFERENCE_DIR / "train_stations.csv"
    st = pd.read_csv(path)
    ex = gpd.read_file(EXITS).to_crs(4326)
    ex["name"] = (ex["STATION_NA"].str.replace(" MRT STATION", "").str.replace(" LRT STATION", "")
                  .str.strip().str.title())
    xy = ex.groupby("name").geometry.agg(lambda g: (g.x.mean(), g.y.mean()))
    st["lon"] = st["name"].map(lambda n: xy[n.title()][0] if isinstance(n, str) and n.title() in xy else None)
    st["lat"] = st["name"].map(lambda n: xy[n.title()][1] if isinstance(n, str) and n.title() in xy else None)
    st.to_csv(path, index=False, float_format="%.6f")
    print(f"  wrote {path.relative_to(config.REPO_ROOT)} ({st['lon'].notna().sum()} stations with coordinates)")


if __name__ == "__main__":
    build_landuse()
    refresh_station_coords()
