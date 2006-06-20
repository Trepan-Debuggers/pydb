# Test of history mechanism
# $Id: history.cmd,v 1.2 2006/06/20 11:06:57 rockyb Exp $
#
set basename on
set cmdtrace on
set history size 5
set history filename
set history filename history.hst
show history
set history save off
set history save on
list
show hi
quit


