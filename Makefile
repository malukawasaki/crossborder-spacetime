PYTHON ?= python
export PYTHONPATH := src

.PHONY: all check reference tables figures test lint

all: check tables figures

check:
	$(PYTHON) scripts/01_check_inputs.py

reference:
	$(PYTHON) scripts/02_build_reference.py

tables:
	$(PYTHON) scripts/03_stage1_bus.py
	$(PYTHON) scripts/04_rhythms.py
	$(PYTHON) scripts/05_stage2_rail.py
	$(PYTHON) scripts/07_paper_numbers.py

figures:
	$(PYTHON) scripts/06_figures.py

test:
	$(PYTHON) -m pytest -q

lint:
	ruff check src scripts tests
