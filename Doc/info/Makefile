# Generate the Python "info" documentation.

TOPDIR=..
TOOLSDIR=$(TOPDIR)/tools
HTMLDIR=$(TOPDIR)/html

# The emacs binary used to build the info docs. GNU Emacs 21 is required.
EMACS=emacs

MKINFO=$(TOOLSDIR)/mkinfo
SCRIPTS=$(TOOLSDIR)/checkargs.pm $(TOOLSDIR)/mkinfo $(TOOLSDIR)/py2texi.el

# set VERSION to code the VERSION number into the info file name
# allowing installation of more than one set of python info docs
# into the same directory
VERSION=

all:	check-emacs-version \
	lib
#	doc inst

lib:	python$(VERSION)-lib.info

whatsnew:	$(WHATSNEW)
$(WHATSNEW):	python$(VERSION)-$(WHATSNEW).info

check-emacs-version:
	@v="`$(EMACS) --version 2>&1 | egrep '^(GNU |X)Emacs [12]*'`"; \
	if `echo "$$v" | egrep '^GNU Emacs 2[1-3]' >/dev/null 2>&1`; then \
	  echo "Using $(EMACS) to build the info docs"; \
	else \
	  echo "GNU Emacs 21 or greater is required to build the info docs"; \
	  echo "Found $$v"; \
	  false; \
	fi

python$(VERSION)-lib.info:	../lib/lib.tex $(SCRIPTS)
	EMACS=$(EMACS) $(MKINFO) $< $*.texi $@

clean:
	rm -f *.texi~ *.texi

clobber: clean
	rm -f *.texi python*-*.info python*-*.info-[0-9]*
