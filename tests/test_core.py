"""Unit tests on synthetic data only (no LTA files needed)."""
import pandas as pd
import pytest

from crossborder import config, io, spacetime, stage1, stage2
from crossborder.stations import station_name


def test_station_name_resolves_composite_and_unknown_codes():
    table = pd.DataFrame({"name": ["Woodlands", "Woodlands", "Kranji"]}, index=["NS9", "TE2", "NS7"])
    assert station_name("NS9/TE2", table) == "Woodlands"
    assert station_name("NS7", table) == "Kranji"
    assert station_name("XX99", table) == "XX99"


@pytest.mark.parametrize("name,sector", [
    ("Raffles Place", "CBD & Civic Core"),
    ("Jurong East", "Secondary Gateways"),
    ("Boon Lay", "Industrial West"),
    ("Tai Seng", "Industrial East"),
    ("Ang Mo Kio", "Northern & Central Heartlands"),
    ("Admiralty", "Other"),
])
def test_sector_classifier(name, sector):
    assert stage2.classify_sector(name) == sector
    assert sector in config.SECTOR_COLOURS


def test_gateways_and_tel_neighbours_are_not_dispersal_destinations():
    assert not stage2.is_dispersal_destination("NS9/TE2")
    assert not stage2.is_dispersal_destination("TE1")
    assert stage2.is_dispersal_destination("EW24/NS1")


def test_period_filter_rejects_other_months():
    ok = pd.DataFrame({"YEAR_MONTH": config.PERIOD})
    assert len(io.filter_period(ok)) == config.N_MONTHS
    with pytest.raises(ValueError, match="outside"):
        io.filter_period(pd.DataFrame({"YEAR_MONTH": config.PERIOD + ["2022-03"]}))
    with pytest.raises(ValueError, match="absent"):
        io.filter_period(pd.DataFrame({"YEAR_MONTH": config.PERIOD[:-1]}))


def test_period_is_ten_months_june_2025_to_march_2026():
    assert config.PERIOD[0] == "2025-06" and config.PERIOD[-1] == "2026-03" and config.N_MONTHS == 10


def test_crossing_speed():
    assert spacetime.crossing_speed_kmh(1.06, 90) == pytest.approx(0.7067, abs=1e-3)
    assert spacetime.crossing_speed_kmh(1.06, 60) == pytest.approx(1.06)
    with pytest.raises(ValueError):
        spacetime.crossing_speed_kmh(1.06, 0)


def test_feeder_split_groups_and_excludes_checkpoint_stops():
    rows = [("46109", "45139", 60), ("46109", "47009", 20), ("46109", "46029", 10), ("46109", "99999", 10),
            ("46109", "46101", 500), ("46101", "46211", 1000)]
    od = pd.DataFrame([{"YEAR_MONTH": "2025-06", "DAY_TYPE": "WEEKDAY", "TIME_PER_HOUR": 7, "PT_TYPE": "BUS",
                        "ORIGIN_PT_CODE": o, "DESTINATION_PT_CODE": d, "TOTAL_TRIPS": t} for o, d, t in rows])
    s = stage1.feeder_split(od).query("day_type == 'ALL'").set_index("destination_group").share_pct
    assert s["Kranji"] == pytest.approx(60)
    assert s["Woodlands"] == pytest.approx(20)
    assert s["Industrial stops"] == pytest.approx(10)
    assert s["Other"] == pytest.approx(10)


def test_corridor_list_has_20_stops_and_uses_47009():
    assert len(config.CORRIDOR_STOPS) == 20 == len(set(config.CORRIDOR_STOPS))
    assert "47009" in config.CORRIDOR_STOPS and "46009" not in config.CORRIDOR_STOPS
