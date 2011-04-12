NAME := turbogears
EPYDOC_PARSE := vigilo\.turbogears\.(controllers\.autocomplete|rum\.fields)

all: build

include buildenv/Makefile.common

install: $(PYTHON) build
	$(PYTHON) setup.py install --record=INSTALLED_FILES
install_pkg: $(PYTHON) build
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR)

lint: lint_pylint
tests: tests_nose
clean: clean_python

.PHONY: install_pkg
