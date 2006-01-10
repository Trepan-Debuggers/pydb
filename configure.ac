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
AM_PATH_LISPDIR
AM_MAINTAINER_MODE
AC_REVISION([$Id: configure.ac,v 1.1 2006/01/10 23:27:42 rockyb Exp $])dnl

dnl make sure we are using a recent autoconf version
AC_PREREQ(2.53)

AC_ARG_PROGRAM
AM_INIT_AUTOMAKE

dnl We use a path for perl so the #! line in autoscan will work.
AC_ARG_WITH(python, AC_HELP_STRING([--with-python], 
		  [location of python program]), PYTHON_PROG=$withval)

if test "$PYTHON_PROG" = "yes" || test "$PYTHON_PROG" = "no" || test -z "$PYTHON_PROG"
then
  AC_PATH_PROG(PYTHON_PROG, python, no)
fi

if test "$PYTHON_PROG" = no; then
  AC_MSG_ERROR([I didn't find the python executable.\
  You might want to use the --with-python option.])
fi

AC_CONFIG_FILES([Makefile])
