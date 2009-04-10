#$Id: Makefile.am,v 1.55 2009/04/10 23:42:02 rockyb Exp $
#   Copyright (C) 2006, 2007, 2008 Rocky Bernstein <rocky@gnu.org>
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

# SUBDIRS = data unit thread 
SUBDIRS = data unit

check_DATA = \
        .pydbrc           \
	brkpt1.cmd        \
	brkpt2.cmd        \
	cmdparse.cmd      \
	comm1.cmd         \
	comm2.cmd         \
	dbgcall.py        \
	except.py         \
	filebug.cmd       \
	filebug.py        \
	gcd.py            \
	hanoi.py          \
	history.cmd       \
	logging.cmd       \
	noscript.cmd      \
	pm.cmd            \
	pydbrc.cmd        \
	run.cmd           \
	run2.cmd          \
	save.cmd          \
	setshow.cmd       \
	settrace.py       \
	sighandler.cmd    \
	skip.cmd          \
	step.cmd          \
        sigtestexample.py \
	withbug.cmd       \
	withbug.py

TESTS = test.py              \
	test-complete.py     \
	test-contbug.py      \
        test-connect.py      \
	test-dbgcall.py      \
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
	test-skip.py         \
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
	file.right.in file-2.5.right.in file.cmd.in \
        settrace.py.in

test: check

clean-generic:
	-rm $(top_builddir)/test/*.pyc \
	$(top_builddir)/test/history.hst \
	$(top_builddir)/test/savefile.txt
