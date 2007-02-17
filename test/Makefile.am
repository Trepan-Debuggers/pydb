#$Id: Makefile.am,v 1.38 2007/02/17 10:53:00 rockyb Exp $
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
	brkpt1t.right     \
	brkpt2.cmd        \
	brkpt2.right      \
	brkpt2-2.3.right  \
	cmdparse.cmd      \
	cmdparse.right    \
	comm1.cmd         \
	comm2.cmd         \
	complete.py       \
	connect.py        \
	contbug.cmd       \
	contbug.py       \
	contbug.right     \
	disassem.py       \
	except.py         \
	filebug.cmd       \
	filebug.py        \
	filebug.right     \
	gcd.py            \
	hanoi.py          \
	history.cmd       \
	history.right     \
	import.py         \
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
	settrace.py       \
	sighandle.py      \
	sighandler.cmd    \
	sighandler.right  \
	sigtest.py        \
        sigtestexample.py \
	test.py           \
	trace-2.5.right   \
	tracetest.py      \
	tracetest.right   \
	tracetest-2.5.right \
	trace.py          \
	trace.right

TESTS = complete.py contbug.py disassem.py file.py \
	fns.py import.py pm.py runtest.py \
	sighandle.py sigtest.py trace.py test.py \
	connect.py tcp_connect.py fifo_connect.py 


EXTRA_DIST = $(check_DATA) brkpt3.cmd.in \
	brkpt3t.right brkpt3.right    \
	complete.py.in contbug.py.in disassem.py.in \
	file.right.in file-2.5.right.in    \
	except.py.in file.cmd.in file.py.in fns.py.in \
        import.py pm.py.in runtest.py.in settrace.py.in test.py.in \
        sighandle.py.in	sigtest.py.in trace.py.in 

test: check

clean-generic:
	-rm $(top_builddir)/test/*.pyc $(top_builddir)/test/history.hst
