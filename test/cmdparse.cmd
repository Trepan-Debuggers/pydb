# $Id: cmdparse.cmd,v 1.3 2006/01/28 01:38:06 rockyb Exp $
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
###  test prompt, misc...
########################################
show prompt
show foo
########################################
###   test numeric argument syntax 
########################################
up fdsafdsa
u=foo
down 1 b c
frame foo
step -1
next -1
### 
quit
