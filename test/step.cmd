# 
# Test of the 'step' and deftrace command
# $Id: step.cmd,v 1.1 2008/05/17 10:08:33 rockyb Exp $
#
set basename on
set trace-commands on
set deftrace off
set listsize 1
step
list
set deftrace on
step
list
set deftrace off
step
list
quit
