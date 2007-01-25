# Test of history mechanism
# $Id: history.cmd,v 1.4 2007/01/25 10:19:15 rockyb Exp $
#
set basename on
set trace-commands on
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


