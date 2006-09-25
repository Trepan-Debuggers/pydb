#$Id: Makefile.am,v 1.27 2006/09/25 00:08:13 rockyb Exp $
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

# SUBDIRS := thread

check_DATA = \
	brkpt1.cmd        \
	brkpt1.right      \
	brkpt2.cmd        \
	brkpt2.right      \
	brkpt3.cmd        \
	brkpt3.right      \
	cmdparse.cmd      \
	cmdparse.right    \
	comm1.cmd         \
	comm2.cmd         \
	connect.py        \
	except.py         \
	file.cmd          \
	file.right        \
	file-2.5.right    \
	filebug.cmd       \
	filebug.py        \
	filebug.right     \
	gcd.py            \
	hanoi.py          \
	history.cmd       \
	history.right     \
	logging.cmd       \
	logging.right     \
	noscript.cmd      \
	noscript.right    \
	pm.cmd            \
	pm.py             \
	pm.right          \
	run.cmd           \
	run.right         \
	run2.cmd          \
	run2.right        \
	sighandle.py      \
	sighandler.cmd    \
	sighandler.right  \
	sigtest.py        \
        sigtestexample.py \
	test.py           \
	trace-2.5.right   \
	trace.py          \
	trace.right

TESTS = fns.py test.py file.py pm.py trace.py sighandle.py sigtest.py \
	connect.py tcp_connect.py fifo_connect.py

EXTRA_DIST = $(check_DATA) except.py.in file.py.in fns.py.in pm.py.in \
	settrace.py.in test.py.in sighandle.py.in sigtest.py.in trace.py.in 

test: check
