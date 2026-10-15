"""Web-Mercator helpers, optional basemap tiles and the land-use background layer."""
import math
from typing import Tuple

import geopandas as gpd

from .. import config

R = 6378137.0


def merc(lon: float, lat: float) -> Tuple[float, float]:
    return R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def lon_label(x, _=None) -> str:
    return f"{math.degrees(x / R):.2f}°E"


def lat_label(y, _=None) -> str:
    return f"{math.degrees(2 * math.atan(math.exp(y / R)) - math.pi / 2):.2f}°N"


def add_basemap(ax) -> bool:
    """Esri World Gray Canvas tiles (no API key) if contextily and a network connection are available."""
    try:
        import contextily as ctx
        ctx.add_basemap(ax, crs="EPSG:3857", source=ctx.providers.Esri.WorldGrayCanvas, zorder=0,
                        attribution_size=6)
        return True
    except Exception as e:  # offline, missing package or tile server error
        print(f"  (basemap skipped: {type(e).__name__})")
        return False


def add_landuse(ax, alpha_strong: float = 0.55, alpha_soft: float = 0.40) -> None:
    lu = gpd.read_file(config.REFERENCE_DIR / "landuse_mp2019.geojson").to_crs(3857)
    for cat, colour in config.LANDUSE_COLOURS.items():
        sub = lu[lu["category"] == cat]
        strong = cat in ("Commercial", "Industrial / Business")
        sub.plot(ax=ax, color=colour, alpha=alpha_strong if strong else alpha_soft, edgecolor="none", zorder=1)
