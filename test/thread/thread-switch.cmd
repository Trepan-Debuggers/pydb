set basename on
step 2
info thread
break 39
info thread terse
continue
frame 0
frame FakeThreadName
frame MainThread
where
# thread Thread-1
# info thread terse
kill unconditionally
