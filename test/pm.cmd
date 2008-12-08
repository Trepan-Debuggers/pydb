# Test of restart and linetracing 
# $Id: pm.cmd,v 1.5 2008/12/08 11:26:27 rockyb Exp $
#
set trace-commands on
set interactive off
set basename on
show args
info args
list
# Completion might not be available if no readline
# complete s
# complete help s
where
step
next
finish
return
quit


