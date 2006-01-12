#$Id: Makefile.am,v 1.8 2006/01/12 09:34:05 rockyb Exp $
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
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# SUBDIRS = test doc emacs
SUBDIRS := emacs

# Basename of debugger, used to form help doc, python script and script
# installed in an executable directory.
DEBUGGER := pydb

# They Python debugger script
python_debugger_script := $(DEBUGGER).py
python_PYTHON := $(DEBUGGER)/$(python_debugger_script)

# The help file
pkgdata_DATA := $(DEBUGGER)/$(DEBUGGER).doc

bin_SCRIPTS := $(DEBUGGER)

# We in fact do install python_PYTHON, just on in the executable directory.
# Instead it's installed with other python programs. The noinst however
# forces a changed pydb.py to get created whenever pydb.py.in changes.
noinst_SCRIPTS := $(python_PYTHON)

# Because we have a *script* called pydb installed in an executable directory
# as well as a python script alas, we just can't need a different installation 
# directory variable. 
pkgdatadir = $(pythondir)
PHONY := $(DEBUGGER)

EXTRA_DIST = ChangeLog TODO $(pkgdata_DATA) \
	     pydb/pydb.doc pydb/Makefile \
	     setup.py site-packages-path.py

# 
# For the executable, we make a symbolic link to the python program,
# and make sure it is executable. Configuration should have put the 
# proper name to the python interpreter into the beginning.
#
install-binSCRIPTS: $(bin_SCRIPTS) install-data-am
	test -z "$(bindir)" || $(mkdir_p) "$(DESTDIR)$(bindir)"
	rm -f "$(DESTDIR)$(bindir)/$(bin_SCRIPTS)" || true;
	chmod +x "$(DESTDIR)$(pythondir)/$(python_debugger_script)"
	$(LN_S) "$(DESTDIR)$(pythondir)/$(python_debugger_script)" "$(DESTDIR)$(bindir)/$(bin_SCRIPTS)"

# cvs2cl
MAINTAINERCLEANFILES = ChangeLog

if MAINTAINER_MODE

PHONY += ChangeLog
ChangeLog:
	$(CVS2CL) -W 450 --header $(srcdir)/cvs2cl_header --utc -w -I ChangeLog --usermap $(srcdir)/cvs2cl_usermap -P 

ACLOCAL_AMFLAGS=-I .

endif

.PHONY: $(PHONY)

#;;; Local Variables: ***
#;;; mode:makefile ***
#;;; End: ***
