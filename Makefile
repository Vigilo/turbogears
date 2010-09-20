NAME := turbogears
EPYDOC_PARSE := vigilo\.turbogears\.controllers\.autocomplete

all: build

include buildenv/Makefile.common

install:
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	chmod a+rX -R $(DESTDIR)$(PREFIX)/lib*/python*/*

lint: lint_pylint
tests: tests_nose
clean: clean_python
