# $Id: cmdparse.cmd,v 1.8 2006/02/27 10:12:20 rockyb Exp $
# This tests the functioning of some debugger command a
# parsing and set/show processing
set basename on
set cmdtrace on
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
show basename
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
set listsize 20
show listsize
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
########################################
###  bad enable disable
########################################
enable 10
disable 10
enable foo
disable foo
########################################
###   test list by number
########################################
list
list
list 10, 15
list 10, 3
list 50
set listsize 6
list 5
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
u=foo
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
help info program
quit
