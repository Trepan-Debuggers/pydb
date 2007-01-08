#$Id: Makefile.am,v 1.45 2007/01/08 12:09:13 rockyb Exp $
#   Copyright (C) 2006 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

SUBDIRS := test emacs

# Basename of debugger, used to form help doc, python script and script
# installed in an executable directory.
DEBUGGER := pydb

# The Python debugger script
python_debugger_script := $(DEBUGGER).py
pkgpython_PYTHON := \
	$(DEBUGGER)/__init__.py \
        $(DEBUGGER)/$(python_debugger_script) \
	$(DEBUGGER)/connection.py  	\
	$(DEBUGGER)/display.py  	\
	$(DEBUGGER)/fns.py		\
	$(DEBUGGER)/gdb.py		\
	$(DEBUGGER)/info.py		\
	$(DEBUGGER)/pydb.py		\
	$(DEBUGGER)/pydbbdb.py		\
	$(DEBUGGER)/pydbcmd.py		\
	$(DEBUGGER)/set.py		\
	$(DEBUGGER)/show.py		\
	$(DEBUGGER)/sighandler.py	\
	$(DEBUGGER)/subcmd.py 		\
	$(DEBUGGER)/threaddbg.py

pkgdata_DATA := $(DEBUGGER)/$(DEBUGGER).doc
pkgdatadir = $(pkgpythondir)

# Section 1 are general commands
EXT=1
man1_MANS = Doc/$(DEBUGGER).$(EXT)

# We in fact do install python_PYTHON, just not in the executable directory.
# Instead it's installed with other python programs. The noinst however
# forces a changed pydb.py to get created whenever pydb.py.in changes.
noinst_SCRIPTS := $(python_PYTHON)

bin_SCRIPTS := $(DEBUGGER)

PHONY := $(DEBUGGER) test

EXTRA_DIST = ChangeLog TODO THANKS        \
	     Doc/Makefile.deps            \
	     Doc/info/Makefile            \
	     pydb/pydb.doc pydb/Makefile  \
	     setup.py setup.py.in site-packages-path.py

MOSTLYCLEANFILES = $(man1_MANS) 

clean-generic: 
	-rm $(top_builddir)/pydb/*.pyc

test: check-recursive
check-recursive: pydb/pydb.py pydb/gdb.py \
	test/connect.py test/fifo_connect.py \
	test/pm.py test/settrace.py test/sighandle.py test/sigtest.py \
	test/tcp_connect.py test/test.py

# 
# For the executable, we make a symbolic link to the python program,
# and make sure it is executable. Configuration should have put the 
# proper name to the python interpreter into the beginning.
#
install-binSCRIPTS: $(bin_SCRIPTS) install-data-am
	if ! test -d "$(DESTDIR)$(bindir)"; then \
	  test -z "$(DESTDIR)$(bindir)" || $(mkdir_p) "$(DESTDIR)$(bindir)"; \
	fi
	rm -f "$(DESTDIR)$(bindir)/$(bin_SCRIPTS)" || true;
	chmod +x "$(DESTDIR)$(pkgpythondir)/$(python_debugger_script)"
	$(LN_S) "$(DESTDIR)$(pkgpythondir)/$(python_debugger_script)" "$(DESTDIR)$(bindir)/$(bin_SCRIPTS)"

# cvs2cl
MAINTAINERCLEANFILES = ChangeLog

if MAINTAINER_MODE

SUBDIRS +=  Doc

EXTRA_DIST +=  \
	Doc/Makefile.deps \
	Doc/Makefile.in \
	Doc/lib/Makefile \
	Doc/lib/lib.tex \
	Doc/lib/libpydb.tex \
	Doc/paper-letter/lib.pdf \
	Doc/paper-letter/lib.ps \
	Doc/perl/SynopsisTable.pm \
	Doc/perl/l2hinit.perl \
	Doc/perl/manual.perl \
	Doc/perl/python.perl \
	Doc/texinputs/fncychap.sty \
	Doc/texinputs/manual.cls \
	Doc/texinputs/pypaper.sty \
	Doc/texinputs/python.ist \
	Doc/texinputs/underscore.sty \
	Doc/tools/getversioninfo \
	Doc/tools/indfix.py \
	Doc/tools/mkhowto \
	Doc/tools/node2label.pl \
	Doc/tools/patchlevel.h \
	Doc/tools/toc2bkm.py

PHONY += ChangeLog
ChangeLog:
	$(CVS2CL) -W 450 --header $(srcdir)/cvs2cl_header --utc -w -I ChangeLog --usermap $(srcdir)/cvs2cl_usermap -P 

ACLOCAL_AMFLAGS=-I .

endif

.PHONY: $(PHONY)

#;;; Local Variables: ***
#;;; mode:makefile ***
#;;; End: ***
