# Copyright (C) 2006, 2007 Rocky Bernstein <rockyb@users.sourceforge.net>

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

AC_REVISION([$Id: configure.ac,v 1.66 2007/04/15 22:27:43 rockyb Exp $])dnl
AC_INIT([pydb],[1.23cvs],[bashdb-pydb-devel@lists.sourceforge.net])
AC_DEFINE([PACKAGE], [pydb], [Python Extended Debugger])
MIN_VERSION='2.4.0'
AC_SUBST(MIN_VERSION)


##
## Find out where to install the debugger emacs lisp files
##
AM_PATH_LISPDIR
AM_CONDITIONAL(INSTALL_EMACS_LISP, test "x$lispdir" != "x")

##
## AM_PATH_PYTHON seems to use PACKAGE and AC_INIT sets PACKAGE_NAME.
if test -z "$PACKAGE" ; then
   PACKAGE=$PACKAGE_NAME
fi

##
## Get user-specified Python site-packages location. This should
## come before getting user-specified Python or looking for that.
##
find_pythondir=yes
AC_ARG_WITH(site-packages,
           AC_HELP_STRING([--with-site-packages], 
	                  [place to install module]), 
	   [pythondir=$withval; 
	   pkgpythondir=${pythondir}/$PACKAGE_NAME
	   find_pythondir=no])
if test "$find_pythondir" != yes; then
   am_cv_python_pythondir=$pythondir
fi

READLINE=readline
AC_ARG_ENABLE(pyreadline,
	AC_HELP_STRING([--enable-pyreadline], 
                        [Use pyreadline instead of readline]),
        [ if test "${enable_readline}" = "yes"; then
	   READLINE=pyreadline
	  fi
	])
AC_SUBST(READLINE)

##
## Get user-specified Python location
##
AM_PATH_LISPDIR
AC_ARG_WITH(python,
           AC_HELP_STRING([--with-python], 
	                  [set path to Python]), 
	   PYTHON=$withval)

##
## Check for Python interpreter and make we have a recent version.
##
AM_PATH_PYTHON($MIN_VERSION,, 
   [AC_MSG_ERROR(Debugger known only to work with Python $MIN_VERSION or greater)])

## Automake doesn't get Python's install path correct. So we 
## figure it out and set it ourself.
## This must come after looking for Python since we use that below.
if test "$find_pythondir" = yes; then
   AC_MSG_NOTICE([Trying to reset site-packages a the default often gets this wrong])
   pythondir=`$PYTHON ${srcdir}/site-packages-path.py`
   if test $? != 0 ; then
      AC_MSG_ERROR([Didn't get Python site packages install path.
      Set it with --with-site-packages])
   fi
   pkgpythondir=\${pythondir}/$PACKAGE_NAME
fi

##
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
## Produced derived files.
##
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([emacs/Makefile])
AC_CONFIG_FILES([test/Makefile])
AC_CONFIG_FILES([Doc/Makefile])
AC_CONFIG_FILES([Doc/pydb.1])
AC_CONFIG_FILES([emacs/pydb-test.el])
AC_CONFIG_FILES([pydb/__init__.py])
AC_CONFIG_FILES([pydb/gdb.py])
AC_CONFIG_FILES([pydb/pydb.py],[chmod +x pydb/pydb.py])
AC_CONFIG_FILES([setup.py],[chmod +x setup.py])
AC_CONFIG_FILES([test/.pydbrc]) # Just to get this into builddir
AC_CONFIG_FILES([test/brkpt3.cmd])
AC_CONFIG_FILES([test/brkpt3.right])
AC_CONFIG_FILES([test/brkpt3t.right])
AC_CONFIG_FILES([test/complete.py],[chmod +x test/complete.py])
AC_CONFIG_FILES([test/connect.py],[chmod +x test/connect.py])
AC_CONFIG_FILES([test/contbug.py],[chmod +x test/contbug.py])
AC_CONFIG_FILES([test/disassem.py],[chmod +x test/disassem.py])
AC_CONFIG_FILES([test/except.py],[chmod +x test/except.py])
AC_CONFIG_FILES([test/exceptbug.py],[chmod +x test/exceptbug.py])
AC_CONFIG_FILES([test/fifo_connect.py],[chmod +x test/fifo_connect.py])
AC_CONFIG_FILES([test/file.cmd])
AC_CONFIG_FILES([test/file.right])
AC_CONFIG_FILES([test/file-2.5.right])
AC_CONFIG_FILES([test/file.py],[chmod +x test/file.py])
AC_CONFIG_FILES([test/fns.py],[chmod +x test/fns.py])
AC_CONFIG_FILES([test/help.py],[chmod +x test/help.py])
AC_CONFIG_FILES([test/import.py],[chmod +x test/import.py])
AC_CONFIG_FILES([test/pm.py],[chmod +x test/pm.py])
AC_CONFIG_FILES([test/runtest.py],[chmod +x test/runtest.py])
AC_CONFIG_FILES([test/settrace.py],[chmod +x test/settrace.py])
AC_CONFIG_FILES([test/sighandle.py], [chmod +x test/sighandle.py])
AC_CONFIG_FILES([test/sigtest.py], [chmod +x test/sigtest.py])
AC_CONFIG_FILES([test/tcp_connect.py],[chmod +x test/tcp_connect.py])
AC_CONFIG_FILES([test/test.py],[chmod +x test/test.py])
AC_CONFIG_FILES([test/trace.py],[chmod +x test/trace.py])
AC_CONFIG_FILES([test/tracetest.py],[chmod +x test/tracetest.py])

AC_OUTPUT
