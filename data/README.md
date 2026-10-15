# Data

## Raw inputs (not redistributed)

The raw files are not stored in this repository. Download them and place them under
`data/raw/` (or point the environment variable `CROSSBORDER_DATA_DIR` at another folder
with the same layout):

```
data/raw/
├── lta/
│   ├── transport_node_bus_YYYYMM.csv        # Passenger Volume by Bus Stops
│   ├── transport_node_train_YYYYMM.csv      # Passenger Volume by Train Stations
│   ├── origin_destination_bus_YYYYMM.csv    # Passenger Volume by Origin Destination Bus Stops
│   ├── origin_destination_train_YYYYMM.csv  # Passenger Volume by Origin Destination Train Stations
│   └── LTAMRTStationExitGEOJSON.geojson     # MRT station exits (only for 02_build_reference.py)
└── ura/
    └── Masterplan2019PBremoved.shp (+ .dbf .shx .prj .cpg)   # only for 02_build_reference.py
```

`YYYYMM` runs from `202506` to `202603` (ten months). The loaders in
`src/crossborder/io.py` read exactly these months and stop with an error if one is
missing or if a file contains other months.

| Dataset | Provider | Where | Used for |
|---|---|---|---|
| Passenger Volume by Bus Stops | Land Transport Authority (LTA) | [LTA DataMall](https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html), Dynamic Datasets API | Tap-ins/tap-outs per stop and hour |
| Passenger Volume by Origin Destination Bus Stops | LTA | LTA DataMall | Causeway crossings, onward trips from Woodlands Checkpoint |
| Passenger Volume by Origin Destination Train Stations | LTA | LTA DataMall | Rail dispersal from the gateway stations |
| Passenger Volume by Train Stations | LTA | LTA DataMall | Input check only |
| Train Station Exit Point | LTA | [data.gov.sg](https://data.gov.sg) | Station coordinates |
| Master Plan 2019 Land Use | Urban Redevelopment Authority (URA) | [data.gov.sg](https://data.gov.sg) | Land-use background |

The passenger-volume datasets are monthly aggregates of fare-card taps by day type
(`WEEKDAY`, `WEEKENDS/HOLIDAY`) and hour (`TIME_PER_HOUR = h` covers `h:00–h:59`). They
contain no individual records. **LTA DataMall only serves the most recent months**, so
the study period can no longer be downloaded from the API; contact the authors if you
need the exact files.

All of these datasets are published under the
[Singapore Open Data Licence](https://data.gov.sg/open-data-licence).

## Committed reference data (`data/reference/`)

Small derived files, so that figures can be drawn without the raw data:

| File | Content | Source |
|---|---|---|
| `train_stations.csv` | Station code, name and coordinates (mean of the exits) for every code in the train OD files | LTA station codes, LTA station exits |
| `bus_stops.csv` | Name and coordinates of the 24 bus stops used in the analysis | LTA DataMall Bus Stops; LTA bus stop locations |
| `landuse_mp2019.geojson` | URA MP2019 land use dissolved into 5 categories and simplified (25 m) | URA Master Plan 2019, built by `scripts/02_build_reference.py` |

Codes without a name (LRT stations PE/PW/SE/SW and a few others) keep their code and fall
into the "Other" sector, as in the manuscript. Stops 47009 (Woodlands Temp Int) and 49259 are not in the
bus stop location file and have no coordinates.

## Commuter profiles (`data/profiles/commuter_profiles.yaml`)

Stylised, pseudonymised daily schedules derived from interviews with cross-border
commuters (see the main README, "Qualitative data").
