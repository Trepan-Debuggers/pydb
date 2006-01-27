check_DATA = \
	cmdparse.cmd \
	cmdparse.right
	test.in

TESTS = test.py

EXTRA_DIST = $(TESTS) $(check_DATA)

test.py: test.py.in
	(cd .. && make test/$@)