#   Copyright (C) 2006, 2008 Rocky Bernstein rockyb@users.sourceforge.net
#
#   Bash is free software; you can redistribute it and/or modify it under
#   the terms of the GNU General Public License as published by the Free
#   Software Foundation; either version 2, or (at your option) any later
#   version.
#
#   Bash is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#   for more details.
#   
#   You should have received a copy of the GNU General Public License along
#   with Bash; see the file COPYING.  If not, write to the Free Software
#   Foundation, 59 Temple Place, Suite 330, Boston, MA 02111 USA.
#$Id: Makefile.am,v 1.14 2008/12/10 13:31:25 rockyb Exp $

check_DATA = pydb-test.el test-gud.el elk-test.el
EXTRA_DIST = pydb.el $(check_DATA)
ELCFILES   = pydb.elc
if INSTALL_EMACS_LISP
lisp_LISP = pydb.el 

check: check-pydb check-gud

check-pydb:
	( cd $(top_srcdir)/emacs && \
	$(EMACS) -batch -q -l $(top_builddir)/emacs/pydb-test.el $(top_srcdir)/emacs/elk-test.el )

check-gud:
	( cd $(top_srcdir)/emacs && \
	$(EMACS) -batch -q -l $(top_srcdir)/emacs/test-gud.el )

test: check
endif
