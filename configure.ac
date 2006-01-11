# Copyright (C) 2006 Rocky Bernstein <rocky@panix.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.

AC_INIT([pydb],[0.1],[pydb-devel@lists.sourceforge.net])
AC_DEFINE([PACKAGE], [pydb], [Python Extended Debugger])
AM_PATH_LISPDIR
AM_PATH_PYTHON(2.4.2,, :)
AM_CONDITIONAL(INSTALL_EMACS_LISP, test "x$lispdir" != "x")
AM_MAINTAINER_MODE
AC_REVISION([$Id: configure.ac,v 1.3 2006/01/11 17:55:01 rockyb Exp $])dnl

dnl make sure we are using a recent autoconf version
AC_PREREQ(2.53)

AC_ARG_PROGRAM
AM_INIT_AUTOMAKE
AM_MISSING_PROG(CVS2CL, cvs2cl, $missing_dir)
AC_PROG_LN_S

pythondir=$($PYTHON_PROG ${srcdir}/site-packages-path.py)
if test $? != 0 ; then
   AC_MSG_ERROR([Didn't get Python site packages install path.])
fi

AC_CONFIG_FILES([Makefile emacs/Makefile \
		 pydb/pydb.py],[chmod +x pydb/pydb.py])

AC_OUTPUT
