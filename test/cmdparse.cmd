# $Id: cmdparse.cmd,v 1.21 2009/03/18 10:15:23 rockyb Exp $
# This tests the functioning of some debugger command a
# parsing and set/show processing
set basename on
set trace-commands on
### *******************************
### ***   Set/show commands     ***
### *******************************
########################################
###   test args and baseneme...
########################################
set args this is a test
show args
show basename
set basename foo
show base
set basename off
show basename
set basename 0
show basename
set basename 1
show basename
########################################
###   test listsize tests...
########################################
show listsize
set listsize 10+10
show listsi
set listsize abc
set listsize -20
set listsize 20 forever
########################################
###  test linetrace...
########################################
set linetrace delay
set linetrace delay 2
show linetrace delay
set linetrace delay 0.5
show linetrace delay
set linetrace delay foo
show linetrace delay
set linetrace on
show linetrace
set linetrace off
show linetrace
show maxargsize
########################################
###  bad enable disable
########################################
enable 10
disable 10
enable foo
disable foo
########################################
###   test list
########################################
list
list
list -
list 10 15
list 10 3
list hanoi.py:12
list hanoi
list hanoi 10
list gcd.py:24
list .
# first and last file names are different
list gcd.py:24 hanoi.py:10
# File doesn't have 50 lines
list 50
set listsi 6
list 5
# Invalid list command - need lineno or fn name
list hanoi.py
########################################
###  test prompt, misc...
########################################
show prompt
show foo
cd
########################################
###   test numeric argument syntax 
########################################
up fdsafdsa
u='foo'
down 1 b c
frame foo
step -1
next -1
########################################
###   test info
########################################
info line
info source
########################################
###   help/info stuff
########################################
help nogood
help restart
help run
help set
help set linesize
help set listsize
help show
help show listsize
help info
#######################################
# The below  "help info" lines should
# have '.' append to the end whereas
# in the above listing they were 
# omitted. 
#######################################
help info program
help info source
#######################################
# The below "help show" commands have 
# more than one line of output also
# ommited in a simple "show"
#######################################
help show args
help show commands
quit
