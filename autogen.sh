#!/bin/sh
#$Id: autogen.sh,v 1.2 2006/01/11 17:55:01 rockyb Exp $
aclocal
automake --add-missing
autoconf
