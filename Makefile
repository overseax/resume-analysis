.PHONY: install test help

install:
	python -m pip install -r requirements.txt
	python -m pip install -e . --no-deps

test:
	python -m pytest

help:
	resume-cli --help
