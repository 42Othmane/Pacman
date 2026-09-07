PYTHON      := python3
PIP         := $(PYTHON) -m pip
VENV        := .venv
CONFIG      ?= config/config.json
MAIN        := main.py

.PHONY: install run debug clean lint lint-strict package

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
	       --ignore-missing-imports --disallow-untyped-defs \
	       --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

package:
	$(PIP) install pyinstaller
	pyinstaller pacman.spec --clean --noconfirm

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist