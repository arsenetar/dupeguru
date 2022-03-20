PYTHON ?= python3
PYTHON_VERSION_MINOR := $(shell ${PYTHON} -c "import sys; print(sys.version_info.minor)")
PYRCC5 ?= pyrcc5
REQ_MINOR_VERSION = 7
PREFIX ?= /usr/local

# Window compatability via Msys2 
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

packages = hscommon qtlib core qt
localedirs = $(wildcard locale/*/LC_MESSAGES)
pofiles = $(wildcard locale/*/LC_MESSAGES/*.po)
mofiles = $(patsubst %.po,%.mo,$(pofiles))

vpath %.po $(localedirs)
vpath %.mo $(localedirs)

all: | env i18n modules qt/dg_rc.py 
	@echo "Build complete! You can run dupeGuru with 'make run'"

run:
	$(VENV_PYTHON) run.py

pyc: | env
	${VENV_PYTHON} -m compileall ${packages}

reqs:
ifneq ($(shell test $(PYTHON_VERSION_MINOR) -ge $(REQ_MINOR_VERSION); echo $$?),0)
	$(error "Python 3.${REQ_MINOR_VERSION}+ required. Aborting.")
endif
ifndef NO_VENV
	@${PYTHON} -m venv -h > /dev/null || \
		echo "Creation of our virtualenv failed. If you're on Ubuntu, you probably need python3-venv."
endif
	@${PYTHON} -c 'import PyQt5' >/dev/null 2>&1 || \
		{ echo "PyQt 5.4+ required. Install it and try again. Aborting"; exit 1; }

env: | reqs
ifndef NO_VENV
	@echo "Creating our virtualenv"
	${PYTHON} -m venv env
	$(VENV_PYTHON) -m pip install -r requirements.txt
# We can't use the "--system-site-packages" flag on creation because otherwise we end up with
# the system's pip and that messes up things in some cases (notably in Gentoo).
	${PYTHON} -m venv --upgrade ${VENV_OPTIONS} env
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
	cp -rf ${packages} locale ${DESTDIR}${PREFIX}/share/dupeguru
	cp -f run.py ${DESTDIR}${PREFIX}/share/dupeguru/run.py
	chmod 755 ${DESTDIR}${PREFIX}/share/dupeguru/run.py
	mkdir -p ${DESTDIR}${PREFIX}/bin
	ln -sf ${PREFIX}/share/dupeguru/run.py ${DESTDIR}${PREFIX}/bin/dupeguru
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
	rm -f "${DESTDIR}${PREFIX}/share/applications/dupeguru.desktop"
	rm -f "${DESTDIR}${PREFIX}/share/pixmaps/dupeguru.png"

clean:
	-rm -rf build
	-rm locale/*/LC_MESSAGES/*.mo
	-rm core/pe/*.$(SO) qt/pe/*.$(SO)

.PHONY: clean normpo mergepot modules i18n reqs run pyc install uninstall all
