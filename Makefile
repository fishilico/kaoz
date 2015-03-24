PACKAGE := kaoz

PYTHON ?= python
# Use current python binary instead of system default for coverage
COVERAGE ?= $(PYTHON) $(shell which coverage)

test:
	$(PYTHON) setup.py test

dist:
	$(PYTHON) setup.py sdist

clean:
	find . -name '*.pyc' -delete
	rm -rf build dist $(PACKAGE).egg-info

coverage:
	$(COVERAGE) erase
	#$(COVERAGE) run "--include=$(PACKAGE)/*.py" --branch setup.py test
	$(COVERAGE) run "--include=$(PACKAGE)/*.py" --branch --parallel-mode kaoz/tests/cover_launch_bot.py
	$(COVERAGE) combine
	$(COVERAGE) report "--include=$(PACKAGE)/*.py"
	$(COVERAGE) html "--include=$(PACKAGE)/*.py"

.PHONY: test dist clean coverage
