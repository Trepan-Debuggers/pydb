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

## Note: the version number (the 2nd parameter in AC_INIT) 
## is picked up inside the Python debugger script.

AC_INIT([pydb],[1.13cvs],[bashdb-pydb-devel@lists.sourceforge.net])
AC_DEFINE([PACKAGE], [pydb], [Python Extended Debugger])

##
## Find out where to install the debugger emacs lisp files
##
AM_PATH_LISPDIR
AM_CONDITIONAL(INSTALL_EMACS_LISP, test "x$lispdir" != "x")

##
## Check for Python interpreter and make we have a recent version.
##
AM_PATH_PYTHON(2.3.5,, :)
AC_REVISION([$Id: configure.ac,v 1.19 2006/02/27 01:02:44 rockyb Exp $])dnl

##
## In maintainer mode we produce a ChangeLog
##
AM_MAINTAINER_MODE

##
## make sure we are using a recent autoconf version
##
AC_PREREQ(2.53)

AC_ARG_PROGRAM
AM_INIT_AUTOMAKE

##
## cvs2cl is used to create the ChangeLog when we create a distribution
##
AM_MISSING_PROG(CVS2CL, cvs2cl, $missing_dir)

##
## A symbolic links is used to link a name in users PATH to the python
## script.
## 
AC_PROG_LN_S

##
## Automake doesn't get Python's install path correct. So we 
## figure it out and set it ourself.
##
AC_ARG_WITH(site-packages,
           AC_HELP_STRING([--with-site-packages], 
	                  [place to install module]), 
	   PY_PKGDIR)

if test -z "$PY_PKGDIR" ; then 
   pythondir=$($PYTHON ${srcdir}/site-packages-path.py)
   if test $? != 0 ; then
      AC_MSG_ERROR([Didn't get Python site packages install path.
      Set it with --with-site-packages])
   fi
   pkgpythondir=\${pythondir}/$PACKAGE
fi

##
## Produced derived files.
##
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([emacs/Makefile])
AC_CONFIG_FILES([test/Makefile])
AC_CONFIG_FILES([Doc/Makefile])
AC_CONFIG_FILES([Doc/pydb.1])
AC_CONFIG_FILES([pydb/__init__.py])
AC_CONFIG_FILES([pydb/pydb.py],[chmod +x pydb/pydb.py])
AC_CONFIG_FILES([test/test.py],[chmod +x test/test.py])
AC_CONFIG_FILES([test/test2.py],[chmod +x test/test2.py])

AC_OUTPUT
