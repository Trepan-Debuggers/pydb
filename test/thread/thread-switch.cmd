set basename on
info thread
break 39
info thread terse
continue
frame 0
frame FakeThreadName
frame MainThread
frame .
where
# thread Thread-1
# info thread terse
kill unconditionally
