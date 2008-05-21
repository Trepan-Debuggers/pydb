#$Id: Makefile.am,v 1.47 2008/05/21 14:48:43 rockyb Exp $
#   Copyright (C) 2006, 2007 Rocky Bernstein
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

# SUBDIRS = thread

check_DATA = \
        .pydbrc           \
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
	contbug.right     \
	contbug-2.5.right \
	except.py         \
	filebug.cmd       \
	filebug.py        \
	filebug.right     \
	fntrace.right     \
	gcd.py            \
	hanoi.py          \
	help.right        \
	history.cmd       \
	history.right     \
	logging.cmd       \
	logging.right     \
	noscript.cmd      \
	noscript.right    \
	pm.cmd            \
	pm.right          \
	pydbrc.cmd           \
	pydbrc.right         \
	run.cmd              \
	run.right            \
	run2.cmd             \
	run2.right           \
	save.cmd             \
	save.right           \
	setshow.cmd          \
	setshow.right        \
	settrace.py          \
	sighandler.cmd       \
	sighandler.right     \
        sigtestexample.py    \
	step.cmd             \
	step.right           \
	trace-2.5.right      \
	trace.right          \
	tracetest-2.5.right  \
	tracetest.right      \
	withbug.cmd          \
	withbug.right

TESTS = test.py              \
	test-complete.py     \
	test-contbug.py      \
        test-connect.py      \
	test-disassem.py     \
        test-file.py         \
	test-fifo-connect.py \
	test-fns.py          \
        test-help.py         \
	test-import.py       \
	test-linetrace.py    \
	test-pm.py           \
	test-run.py          \
        test-setshow.py      \
        test-sig.py          \
	test-sighandle.py    \
	test-save.py         \
	test-step.py         \
        test-trace.py        \
	test-tcp-connect.py  \
	test-trace.py        \
	test-with.py

EXTRA_DIST = \
	$(check_DATA) \
	$(patsubst %.py,%.py.in, $(TESTS)) \
	brkpt3.cmd.in \
	.pydbrc.in \
	brkpt3t.right brkpt3-2.5t.right brkpt3.right    \
	file.right.in file-2.5.right.in file.cmd.in \
        settrace.py.in

test: check

clean-generic:
	-rm $(top_builddir)/test/*.pyc $(top_builddir)/test/history.hst
