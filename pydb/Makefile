#=============================================================
# $Id: Makefile,v 1.2 2006/02/27 01:02:47 rockyb Exp $
#=============================================================
# Whatever it is you want to do, it should be handled by the 
# by the main (parent) Makefile. So reissue make from there.
.PHONY: all

all: pydb.py
	$(MAKE) -C .. $@

pydb.py: pydb.py.in
	$(MAKE) -C .. pydb/$@

%: 
	$(MAKE) -C .. $@

