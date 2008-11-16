def foo():
    """Exception to raise to quit debugging.

FIXME: we allow stopping here but we shouldn't
"""
    return

# Should not allow stopping here
print "hi"
