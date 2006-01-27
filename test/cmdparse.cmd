# $Id: cmdparse.cmd,v 1.2 2006/01/27 18:35:00 rockyb Exp $
# This tests the functioning of some debugger command a
# parsing and set/show processing
print "********************************"
print "***   Set/show commands     ***"
print "*******************************"
########################################
print "  test args and baseneme..."
########################################
set args this is a test
show args
set basename on
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
print "  test listsize tests..."
########################################
show listsize
set listsize 20
show listsize
set listsize abc
set listsize -20
set listsize 20 forever
########################################
print "  test linetrace..."
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
print "  test prompt, misc..."
########################################
show prompt
show foo
########################################
print "  test numeric argument syntax "
########################################
up fdsafdsa
u=foo
down 1 b c
frame foo
step -1
next -1
### 
quit
