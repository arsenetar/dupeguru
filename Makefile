PYTHON ?= python3
PYTHON_VERSION_MINOR := $(shell ${PYTHON} -c "import sys; print(sys.version_info.minor)")
PYRCC5 ?= pyrcc5
REQ_MINOR_VERSION = 7
PREFIX ?= /usr/local
# REDIS_HOST ?= 192.168.2.249:6379
# REDIS_DB ?= 1
# REDIS_PASS ?=
REDIS_HOST ?=
REDIS_DB ?= 1
REDIS_PASS ?=

ifeq ($(REDIS_PASS),)
	REDIS_URL = redis://$(REDIS_HOST)/$(REDIS_DB)
else
	REDIS_URL = redis://:$(REDIS_PASS)@$(REDIS_HOST)/$(REDIS_DB)
endif

USE_REDIS ?=
ifneq ($(USE_REDIS),)
	WEB_ENV = DUPEGURU_CACHE_URL="$(REDIS_URL)"
else
	ifneq ($(REDIS_PASS),)
		WEB_ENV = DUPEGURU_CACHE_URL="$(REDIS_URL)"
	else
		WEB_ENV =
	endif
endif

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
	@echo "de-dup Build & Management Tool"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Primary Targets:"
	@echo "  help           Print this help message"
	@echo "  all            Build all components (virtualenv, i18n, C modules, Qt resources, Rust engine)"
	@echo "  run            Run the de-dup Qt desktop application"
	@echo "  web            Run the de-dup HTML Web Console REST server and launch browser"
	@echo "  rust           Compile the Rust parallel engine shared library (dupeguru_rust.so)"
	@echo "  modules        Compile high-performance C extension modules"
	@echo "  env            Create virtual environment and install dependencies using uv"
	@echo "  pyc            Compile Python source code to bytecode"
	@echo ""
	@echo "Documentation Targets:"
	@echo "  docs-serve     Run local live-reloading documentation site at http://localhost:8000"
	@echo "  docs-build     Build static HTML documentation site to site/ directory"
	@echo "  installdocs    Build and install HTML help documentation to system path"
	@echo ""
	@echo "Database & Cache Targets:"
	@echo "  db-to-redis    Convert local SQLite database to Valkey/Redis cache instance"
	@echo "  redis-to-db    Convert Valkey/Redis cache instance to local SQLite database"
	@echo ""
	@echo "Installation & Packaging:"
	@echo "  install        Install de-dup to system path (PREFIX=/usr/local)"
	@echo "  uninstall      Uninstall de-dup from system path"
	@echo "  package        Create standalone native executable package for current OS"
	@echo ""
	@echo "Localization (i18n):"
	@echo "  i18n           Compile all localization (.po to .mo) translation files"
	@echo "  mergepot       Regenerate and merge gettext (.pot) translation templates"
	@echo "  normpo         Normalize and format .po translation files"
	@echo ""
	@echo "Maintenance & Development:"
	@echo "  clean          Clean up build artifacts, virtualenv, and compiled extensions"
	@echo "  dev-setup      Interactive setup for dev environment (uv, system packages, pre-commit)"
	@echo "  release-status Show current release version alignment status"
	@echo "  tag            Create release git tag (e.g. make tag TAG=1.2.3)"
	@echo ""

all: | env i18n modules qt/dg_rc.py rust
	@echo "Build complete! You can run dupeGuru with 'make run'"

run:
	$(VENV_PYTHON) run.py

web: all
	$(WEB_ENV) $(VENV_PYTHON) -u run_web.py

docs-serve:
	$(VENV_PYTHON) -m mkdocs serve

docs-build:
	$(VENV_PYTHON) -m mkdocs build

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

RUST_SRCS = $(wildcard rust_engine/src/*.rs) rust_engine/Cargo.toml

ifeq ($(shell ${PYTHON} -c "import platform; print(platform.system())"), Windows)
RUST_SO = core/dupeguru_rust.pyd
RUST_TARGET_SO = rust_engine/target/release/dupeguru_rust.dll
else
RUST_SO = core/dupeguru_rust.so
RUST_TARGET_SO = rust_engine/target/release/libdupeguru_rust.so
endif

$(RUST_SO): $(RUST_SRCS)
	cd rust_engine && cargo build --release
	cp $(RUST_TARGET_SO) $(RUST_SO)

rust: $(RUST_SO)


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
	-rm -f core/dupeguru_rust.$(SO)
	-cd rust_engine && cargo clean

db-to-redis:
	@echo "Converting SQLite DB to Redis/Valkey at $(REDIS_URL)..."
	$(VENV_PYTHON) scripts/convert_cache.py ~/.local/share/dupeGuru/hash_cache.db $(REDIS_URL) $(FLAGS)

redis-to-db:
	@echo "Converting Redis/Valkey at $(REDIS_URL) to SQLite DB..."
	$(VENV_PYTHON) scripts/convert_cache.py $(REDIS_URL) ~/.local/share/dupeGuru/hash_cache_new.db $(FLAGS)

dev-setup:
	@echo "Setting up development environment..."
	@if ! command -v uv >/dev/null 2>&1; then \
		printf "uv is not installed. Do you want to install it from https://astral.sh? [y/N]: "; \
		read answer; \
		if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
			echo "Installing uv..."; \
			curl -LsSf https://astral.sh/uv/install.sh | sh; \
		else \
			echo "Skipping uv installation. Please install uv manually to continue."; \
			exit 1; \
		fi; \
	else \
		echo "uv is already installed."; \
	fi
	@if [ "$$(uname)" = "Linux" ] && command -v apt-get >/dev/null 2>&1; then \
		missing=""; \
		if ! command -v pyrcc5 >/dev/null 2>&1; then missing="$$missing python3-pyqt5 pyqt5-dev-tools"; fi; \
		if ! dpkg -s python3-dev >/dev/null 2>&1; then missing="$$missing python3-dev"; fi; \
		if ! dpkg -s build-essential >/dev/null 2>&1; then missing="$$missing build-essential"; fi; \
		if [ -n "$$missing" ]; then \
			echo "The following system packages are missing:$$missing"; \
			printf "Do you want to install them via apt? (Requires sudo) [y/N]: "; \
			read answer; \
			if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
				sudo apt-get update && sudo apt-get install -y $$missing; \
			else \
				echo "Skipping system packages installation. Some build steps may fail."; \
			fi; \
		fi; \
	fi
	@$(MAKE) env
	@if [ -f ./env/bin/pre-commit ]; then \
		printf "Do you want to install the pre-commit git hooks? [y/N]: "; \
		read answer; \
		if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
			echo "Installing pre-commit hooks..."; \
			./env/bin/pre-commit install; \
		else \
			echo "Skipping pre-commit hooks installation."; \
		fi; \
	else \
		echo "pre-commit was not found in the virtual environment. Skipping hooks setup."; \
	fi
	@echo "Development environment setup complete!"

.PHONY: help clean normpo mergepot modules i18n reqs run web docs-serve docs-build rust package release-status tag pyc install installdocs uninstall all dev-setup db-to-redis redis-to-db
