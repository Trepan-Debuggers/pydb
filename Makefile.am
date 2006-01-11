#$Id: Makefile.am,v 1.3 2006/01/11 17:55:01 rockyb Exp $
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

DEBUGGER := pydb
python_DEBUGGER := $(DEBUGGER).py
python_PYTHON := pydb/$(DEBUGGER).py
bin_SCRIPTS := $(DEBUGGER)
pkgdata_DATA := pydb/$(DEBUGGER).doc
pkgdatadir = $(pythondir)
PHONY := $(DEBUGGER)

EXTRA_DIST = ChangeLog $(pkgdata_DATA)

install-binSCRIPTS: $(bin_SCRIPTS) install-data-am
	test -z "$(bindir)" || $(mkdir_p) "$(DESTDIR)$(bindir)"
	rm -f "$(DESTDIR)$(bindir)/$(bin_SCRIPTS)" || true;
	chmod +x "$(DESTDIR)$(pythondir)/$(python_DEBUGGER)"
	$(LN_S) "$(DESTDIR)$(pythondir)/$(python_DEBUGGER)" "$(DESTDIR)$(bindir)/$(bin_SCRIPTS)"

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
