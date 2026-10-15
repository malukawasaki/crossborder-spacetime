"""Draw all figures from the committed tables in results/tables (no raw data needed)."""
import sys

from crossborder.plotting import figures

wanted = set(sys.argv[1:])
for fn in figures.ALL:
    if not wanted or fn.__name__ in wanted:
        print(fn.__name__)
        fn()
