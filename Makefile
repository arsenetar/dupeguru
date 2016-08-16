PYTHON=python3
REQ_MINOR_VERSION=4

# Our build scripts are not very "make like" yet and perform their task in a bundle. For now, we
# use one of each file to act as a representative, a target, of these groups.
pemodules_target = core/pe/_block.*.so
mofiles_target = locale/fr/LC_MESSAGES/core.mo
submodules_target = hscommon/__init__.py

pofiles = $(wildcard locale/*/LC_MESSAGES/*.po)

.PHONY : default
default : run.py
	@echo "Build complete! You can run dupeGuru with 'make run'"

run.py : env $(mofiles_target) $(pemodules_target) qt/dg_rc.py
	cp qt/run_template.py run.py

.PHONY : reqs
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
	./env/bin/pip install -r requirements.txt

build/help : | env
	./env/bin/python build.py --doc

qt/dg_rc.py : qt/dg.qrc
	pyrcc5 qt/dg.qrc > qt/dg_rc.py

$(mofiles_target) : $(pofiles) | env
	./env/bin/python build.py --loc
	
$(pemodules_target) :
	./env/bin/python -c 'import build; build.build_pe_modules("qt")'

.PHONY : mergepot
mergepot :
	./env/bin/python build.py --mergepot

.PHONY : normpo
normpo :
	./env/bin/python build.py --normpo

.PHONY : run
run: run.py
	./env/bin/python run.py

.PHONY : clean
clean:
	-rm run.py
	-rm -rf build
	-rm locale/*/LC_MESSAGES/*.mo
