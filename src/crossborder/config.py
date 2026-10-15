"""Study-wide constants: period, time windows, stop/station codes, coordinates and colours.

Every number that defines *what is measured* lives here, so that each table and figure
is traceable to one definition.
"""
import os
from pathlib import Path

# --------------------------------------------------------------------------- paths
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("CROSSBORDER_DATA_DIR", REPO_ROOT / "data" / "raw"))
REFERENCE_DIR = REPO_ROOT / "data" / "reference"
PROFILES_FILE = REPO_ROOT / "data" / "profiles" / "commuter_profiles.yaml"
TABLES_DIR = REPO_ROOT / "results" / "tables"
FIGURES_DIR = REPO_ROOT / "results" / "figures"

# --------------------------------------------------------------------------- study period
# Ten consecutive months, June 2025 - March 2026 (LTA YEAR_MONTH format).
PERIOD = [f"2025-{m:02d}" for m in range(6, 13)] + [f"2026-{m:02d}" for m in range(1, 4)]
N_MONTHS = len(PERIOD)

# LTA convention: TIME_PER_HOUR = h covers h:00-h:59.
AM_PEAK_HOURS = [6, 7, 8, 9]          # 06:00-09:59, weekday rail dispersal window
AM_PEAK_SENSITIVITY_HOURS = [6, 7, 8]  # 06:00-08:59
WEEKDAY = "WEEKDAY"

# --------------------------------------------------------------------------- bus stops
# Woodlands Checkpoint has two bus stops on the Singapore side:
WDL_CP_FROM_JB = "46109"  # arrivals from JB alight and board onward Singapore buses here
WDL_CP_TO_JB = "46101"    # Singapore -> JB: passengers alight from local buses, board for JB
JB_CP_TO_SG = "46219"     # JB Checkpoint, boarding towards Singapore
JB_CP_FROM_SG = "46211"   # JB Checkpoint, alighting from Singapore
CHECKPOINT_STOPS = [WDL_CP_FROM_JB, WDL_CP_TO_JB, JB_CP_TO_SG, JB_CP_FROM_SG]

# Stage 1 feeder destinations, grouped to the MRT gateway they serve.
# Gateway letters follow the map: A = Kranji, B = Marsiling, C = Woodlands.
GATEWAYS = {
    "Kranji": {"letter": "A", "station": "NS7", "bus_stops": ["45139", "45131"]},
    "Marsiling": {"letter": "B", "station": "NS8", "bus_stops": ["46521", "46529"]},
    # 47009 Woodlands Temp Int is the stop served from the checkpoint; 46009 receives no
    # checkpoint trips in the bus OD data.
    "Woodlands": {"letter": "C", "station": "NS9/TE2", "bus_stops": ["47009"]},
}

# The 13 "industrial" stops used in the manuscript, grouped and labelled by the actual
# stop names (data/reference/bus_stops.csv). Note that Woodlands Ave 3 (Marsiling Mall,
# Blk 347) is a residential/retail location and Kranji Lodge is a workers' dormitory.
INDUSTRIAL_CLUSTERS = {
    "Kranji Loop / Kranji Way": ["49259", "49149", "49179"],
    "Woodlands Ind Pk D / Kranji Lodge": ["46029", "46039"],
    "GlobalFoundries (Woodlands Rd)": ["46059", "46049", "46041"],
    "Woodlands Ave 3 (Marsiling)": ["46541", "46549"],
    "Admiralty Rd West": ["47031", "47029", "47021"],
}
INDUSTRIAL_STOPS = [s for stops in INDUSTRIAL_CLUSTERS.values() for s in stops]

# 20-stop "corridor" used for the aggregate tap-out volume (gateway feeder stops,
# JB Checkpoint and nearby industrial stops).
CORRIDOR_STOPS = (
    [s for g in GATEWAYS.values() for s in g["bus_stops"]]
    + [JB_CP_FROM_SG, JB_CP_TO_SG]
    + INDUSTRIAL_STOPS
)

# --------------------------------------------------------------------------- train stations
GATEWAY_STATIONS = {g["station"]: name for name, g in GATEWAYS.items()}
# Destinations excluded from Stage 2 dispersal: the gateways themselves and the other
# Woodlands TEL stations (TE1 Woodlands North, TE3 Woodlands South).
NON_DISPERSAL_CODES = {"NS7", "NS8", "NS9", "TE1", "TE2", "TE3"}

# --------------------------------------------------------------------------- coordinates (lon, lat)
COORDS = {
    "JB CIQ": (103.7632, 1.4621),
    "Woodlands Checkpoint": (103.7637, 1.4477),
    "JB Home": (103.7578, 1.4655),
    "Kranji MRT": (103.7179, 1.4252),
    "Orchard": (103.8318, 1.3040),
}
# Industrial cluster positions are the mean of their bus-stop coordinates (data/reference/bus_stops.csv).
SECTOR_COORDS = {
    "CBD & Civic Core": (103.8520, 1.2930),
    "Secondary Gateways": (103.7436, 1.3329),
    "Industrial West": (103.6800, 1.3200),
    "Industrial East": (103.8884, 1.3349),
    "Northern & Central Heartlands": (103.8485, 1.3691),
}
MAP_EXTENT = (103.62, 103.98, 1.25, 1.48)  # lon_min, lon_max, lat_min, lat_max

# --------------------------------------------------------------------------- colours
SECTOR_COLOURS = {
    "CBD & Civic Core": "#1d4ed8",
    "Secondary Gateways": "#0f766e",
    "Industrial West": "#6b21a8",
    "Industrial East": "#9333ea",
    "Northern & Central Heartlands": "#d97706",
    "Other": "#94a3b8",
}
LANDUSE_COLOURS = {
    "Commercial": "#2563eb",
    "Industrial / Business": "#a855f7",
    "Residential": "#fef08a",
    "Parks & Open Space": "#bbf7d0",
    "Civic & Institutional": "#cbd5e1",
}
DIRECTION_COLOURS = {"JB -> SG": "#dc2626", "SG -> JB": "#2563eb"}
