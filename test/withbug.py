from __future__ import with_statement
    
class FakeClass:

    def __init__(self):
        x = 1
        return
    
    def __enter__(self):
        return 1

    def __exit__(self, type, value, traceback):
        return 2

def test():
  with FakeClass() as f:
      print f
      return
  return

test()

