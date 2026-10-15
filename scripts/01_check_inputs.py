"""Check that every raw input needed for the study period is present."""
import sys

from crossborder import config, io

MP2019 = config.DATA_DIR / "ura" / "Masterplan2019PBremoved.shp"
EXITS = config.DATA_DIR / "lta" / "LTAMRTStationExitGEOJSON.geojson"


def main() -> int:
    ok = True
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Study period:   {config.PERIOD[0]} .. {config.PERIOD[-1]} ({config.N_MONTHS} months)")
    for family in io.FAMILIES:
        try:
            files = io.period_files(family)
            print(f"  ok   {family:26s} {len(files)} files")
        except FileNotFoundError as e:
            ok = False
            print(f"  MISSING {e}")
    for f in (MP2019, EXITS):
        print(f"  {'ok  ' if f.exists() else 'MISSING'} {f.relative_to(config.DATA_DIR)}"
              f"{'' if f.exists() else '  (only needed for 02_build_reference.py)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
