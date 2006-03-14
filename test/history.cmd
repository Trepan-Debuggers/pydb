# Test of history mechanism
# $Id: history.cmd,v 1.1 2006/03/14 03:48:47 rockyb Exp $
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
show history
quit


