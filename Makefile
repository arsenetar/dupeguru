PYTHON ?= python3
REQ_MINOR_VERSION = 4
PREFIX ?= /usr/local

# If you're installing into a path that is not going to be the final path prefix (such as a
# sandbox), set DESTDIR to that path.

# Our build scripts are not very "make like" yet and perform their task in a bundle. For now, we
# use one of each file to act as a representative, a target, of these groups.
submodules_target = hscommon/__init__.py

packages = hscommon qtlib core qt
localedirs = $(wildcard locale/*/LC_MESSAGES)
pofiles = $(wildcard locale/*/LC_MESSAGES/*.po)
mofiles = $(patsubst %.po,%.mo,$(pofiles))

vpath %.po $(localedirs)
vpath %.mo $(localedirs)

all : | env i18n modules qt/dg_rc.py
	@echo "Build complete! You can run dupeGuru with 'make run'"

run:
	./env/bin/python run.py

pyc:
	${PYTHON} -m compileall ${packages}

reqs :
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi
	@${PYTHON} -m venv -h > /dev/null || \
		echo "Creation of our virtualenv failed. If you're on Ubuntu, you probably need python3-venv."
	@${PYTHON} -c 'import PyQt5' >/dev/null 2>&1 || \
		{ echo "PyQt 5.4+ required. Install it and try again. Aborting"; exit 1; }

# Ensure that submodules are initialized
$(submodules_target) :
	git submodule init
	git submodule update

env : | $(submodules_target) reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv env --system-site-packages
	./env/bin/python -m pip install -r requirements.txt

build/help : | env
	./env/bin/python build.py --doc

qt/dg_rc.py : qt/dg.qrc
	pyrcc5 qt/dg.qrc > qt/dg_rc.py

i18n: $(mofiles)

%.mo : %.po
	msgfmt -o $@ $<	

core/pe/_block.*.so : core/pe/modules/block.c core/pe/modules/common.c | env
	./env/bin/python hscommon/build_ext.py $^ _block
	mv _block.*.so core/pe

core/pe/_cache.*.so : core/pe/modules/cache.c core/pe/modules/common.c | env
	./env/bin/python hscommon/build_ext.py $^ _cache
	mv _cache.*.so core/pe

qt/pe/_block_qt.*.so : qt/pe/modules/block.c | env
	./env/bin/python hscommon/build_ext.py $^ _block_qt
	mv _block_qt.*.so qt/pe

modules : core/pe/_block.*.so core/pe/_cache.*.so qt/pe/_block_qt.*.so

mergepot :
	./env/bin/python build.py --mergepot

normpo :
	./env/bin/python build.py --normpo

srcpkg :
	./scripts/srcpkg.sh

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

uninstall :
	rm -rf "${DESTDIR}${PREFIX}/share/dupeguru"
	rm -f "${DESTDIR}${PREFIX}/bin/dupeguru"
	rm -f "${DESTDIR}${PREFIX}/share/applications/dupeguru.desktop"
	rm -f "${DESTDIR}${PREFIX}/share/pixmaps/dupeguru.png"

clean:
	-rm -rf build
	-rm locale/*/LC_MESSAGES/*.mo
	-rm core/pe/*.so qt/pe/*.so

.PHONY : clean srcpkg normpo mergepot modules i18n reqs run pyc install uninstall all
