#!/usr/bin/make -f

all:
	dh_prep  
	dh_installdirs
	touch build_pe_modules.py
	python3 build_pe_modules.py
	chmod +x src/run.py
	cp -R src/ $(CURDIR)/debian/{pkgname}/usr/share/{execname}
	cp $(CURDIR)/debian/{execname}.desktop $(CURDIR)/debian/{pkgname}/usr/share/applications
	ln -s /usr/share/{execname}/run.py $(CURDIR)/debian/{pkgname}/usr/bin/{execname}