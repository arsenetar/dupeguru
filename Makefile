PYTHON ?= python3
PYTHON_VERSION_MINOR := $(shell ${PYTHON} -c "import sys; print(sys.version_info.minor)")
PYRCC5 ?= pyrcc5
REQ_MINOR_VERSION = 7
PREFIX ?= /usr/local

# Window compatibility via Msys2
# - venv creates Scripts instead of bin
# - compile generates .pyd instead of .so
# - venv with --sytem-site-packages has issues on windows as well...

ifeq ($(shell ${PYTHON} -c "import platform; print(platform.system())"), Windows)
	BIN = Scripts
	SO = *.pyd
	VENV_OPTIONS =
else
	BIN = bin
	SO = *.so
	VENV_OPTIONS = --system-site-packages
endif

# Set this variable if all dependencies are already met on the system. We will then avoid the
# whole vitualenv creation and pip install dance.
NO_VENV ?=

ifdef NO_VENV
	VENV_PYTHON = $(PYTHON)
else
	VENV_PYTHON = ./env/$(BIN)/python
endif

# If you're installing into a path that is not going to be the final path prefix (such as a
# sandbox), set DESTDIR to that path.

# Our build scripts are not very "make like" yet and perform their task in a bundle. For now, we
# use one of each file to act as a representative, a target, of these groups.

packages = hscommon core qt
localedirs = $(wildcard locale/*/LC_MESSAGES)
pofiles = $(wildcard locale/*/LC_MESSAGES/*.po)
mofiles = $(patsubst %.po,%.mo,$(pofiles))

vpath %.po $(localedirs)
vpath %.mo $(localedirs)

.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo "  help         Print this help message"
	@echo "  all          Build all components (virtualenv, i18n, C modules, Qt resources)"
	@echo "  run          Run the dupeGuru application in the virtual environment"
	@echo "  web          Run the dupeGuru HTML Web Console interface"
	@echo "  pyc          Compile Python source code to bytecode"
	@echo "  env          Create the virtual environment and install dependencies using uv"
	@echo "  modules      Compile high-performance C extension modules"
	@echo "  i18n         Compile all localization (.po to .mo) files"
	@echo "  clean        Clean up build files, compiled extensions, and localizations"
	@echo "  install      Install dupeGuru to the system (controlled by PREFIX/DESTDIR)"
	@echo "  uninstall    Uninstall dupeGuru from the system"
	@echo "  package      Create a standalone native executable package for the current OS"
	@echo "  tag          Create tag for a release; Example: make tag TAG=1.2.3"
	@echo "  release-status Show current release version status and changelog alignment"

all: | env i18n modules qt/dg_rc.py
	@echo "Build complete! You can run dupeGuru with 'make run'"

run:
	$(VENV_PYTHON) run.py

web: | all
	$(VENV_PYTHON) run_web.py

package: | all
	$(VENV_PYTHON) package.py

release-status:
	$(VENV_PYTHON) scripts/release_helper.py status

tag:
	@if [ -z "$(TAG)" ]; then \
		printf "Enter version for release tag (e.g., 4.3.2): "; \
		read tag_val; \
	else \
		tag_val="$(TAG)"; \
	fi; \
	if [ -z "$$tag_val" ]; then \
		echo "Error: Release version cannot be empty."; \
		exit 1; \
	fi; \
	$(VENV_PYTHON) scripts/release_helper.py release $$tag_val

pyc: | env
	${VENV_PYTHON} -m compileall ${packages}

reqs:
ifneq ($(shell test $(PYTHON_VERSION_MINOR) -ge $(REQ_MINOR_VERSION); echo $$?),0)
	$(error "Python 3.${REQ_MINOR_VERSION}+ required. Aborting.")
endif

env: | reqs
ifndef NO_VENV
	@echo "Creating virtualenv with uv"
	uv venv $(VENV_OPTIONS) --allow-existing env
	VIRTUAL_ENV=env uv pip install -e .[dev]
endif


build/help: | env
	$(VENV_PYTHON) build.py --doc

qt/dg_rc.py: qt/dg.qrc
	$(PYRCC5) qt/dg.qrc > qt/dg_rc.py

i18n: $(mofiles)

%.mo: %.po
	msgfmt -o $@ $<

modules: | env
	$(VENV_PYTHON) build.py --modules

mergepot: | env
	$(VENV_PYTHON) build.py --mergepot

normpo: | env
	$(VENV_PYTHON) build.py --normpo

install: all pyc
	mkdir -p ${DESTDIR}${PREFIX}/share/dupeguru
	cp -rf ${packages} locale web ${DESTDIR}${PREFIX}/share/dupeguru
	cp -f run.py ${DESTDIR}${PREFIX}/share/dupeguru/run.py
	cp -f run_web.py ${DESTDIR}${PREFIX}/share/dupeguru/run_web.py
	chmod 755 ${DESTDIR}${PREFIX}/share/dupeguru/run.py
	chmod 755 ${DESTDIR}${PREFIX}/share/dupeguru/run_web.py
	mkdir -p ${DESTDIR}${PREFIX}/bin
	ln -sf ${PREFIX}/share/dupeguru/run.py ${DESTDIR}${PREFIX}/bin/dupeguru
	ln -sf ${PREFIX}/share/dupeguru/run_web.py ${DESTDIR}${PREFIX}/bin/dupeguru-web
	mkdir -p ${DESTDIR}${PREFIX}/share/applications
	cp -f pkg/dupeguru.desktop ${DESTDIR}${PREFIX}/share/applications
	mkdir -p ${DESTDIR}${PREFIX}/share/pixmaps
	cp -f images/dgse_logo_128.png ${DESTDIR}${PREFIX}/share/pixmaps/dupeguru.png

installdocs: build/help
	mkdir -p ${DESTDIR}${PREFIX}/share/dupeguru
	cp -rf build/help ${DESTDIR}${PREFIX}/share/dupeguru

uninstall:
	rm -rf "${DESTDIR}${PREFIX}/share/dupeguru"
	rm -f "${DESTDIR}${PREFIX}/bin/dupeguru"
	rm -f "${DESTDIR}${PREFIX}/bin/dupeguru-web"
	rm -f "${DESTDIR}${PREFIX}/share/applications/dupeguru.desktop"
	rm -f "${DESTDIR}${PREFIX}/share/pixmaps/dupeguru.png"

clean:
	-rm -rf build
	-rm -rf .venv env
	-rm -f locale/*/LC_MESSAGES/*.mo
	-rm -f core/pe/*.$(SO) qt/pe/*.$(SO)

.PHONY: help clean normpo mergepot modules i18n reqs run web package release-status tag pyc install uninstall all
