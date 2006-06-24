# Test of history mechanism
# $Id: history.cmd,v 1.3 2006/06/24 08:47:02 rockyb Exp $
#
set basename on
set cmdtrace on
set history size 5
set history filename
set history filename history.hst
show history
#########################################
# Test save on and off.
# Test also using short abbreviated name
#########################################
set his save off
set hi save on
list
show hi
quit


