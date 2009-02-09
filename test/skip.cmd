# 
# Test of the 'step' and deftrace command
# $Id: skip.cmd,v 1.1 2009/02/09 09:28:39 rockyb Exp $
#
set basename on
set trace-commands on
set deftrace off
set linetrace on
set listsize 1
skip
list
p sys
skip foo
skip 2
c 38
skip
list
quit
