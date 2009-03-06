# -*- coding: utf-8 -*-
"""Classes to support gdb-like display/undisplay.
$Id: display.py,v 1.5 2009/03/06 09:41:37 rockyb Exp $"""

import fns

def signature(frame):
    '''return suitable frame signature to key display expressions off of.'''
    if not frame: return None
    code = frame.f_code
    return (code.co_name, code.co_filename, code.co_firstlineno)

class Display:
    '''Manage a list of display expressions.'''
    def __init__(self):
        self.next = 0
        self.list = []
        return

    def all(self):
        """List all display items; return 0 if none"""
        any = 0
        for dp in self.list:
            if not any:
                print """Auto-display expressions now in effect:
Num Enb Expression"""
                any = 1
            dp.params()
        return any

    def clear(self):
        """Delete all display expressions"""
        self.list = []
        return

    def delete_index(self, i):
        """Delete display expression i"""
        for dp in self.list:
            if i == dp.number:
                dp.deleteMe()
                return
            pass
        return

    def display(self, frame):
        '''display any items that are active'''
        if not frame: return
        sig = signature(frame)
        for display in self.list:
            if display.code == sig and display.enabled:
                print display.displayMe(frame)
                pass
            pass
        return

    def enable_disable(self, i, b_enable_dispable):
        for display in self.list:
            if i == display.number:
                if b_enable_disable:
                   dp.enableMe()
                else:
                   dp.disableMe()
                return
            pass
        return

    pass

class DisplayNode(Display):

    def __init__(self, frame, arg, fmt):
        Display.__init(self)
        self.code = signature(frame)
        self.fmt = fmt
        self.arg = arg
        self.enabled = True
        super.next += 1
        self.number = super.next
        super.list.append(self)

    def displayMe(self, frame):
        if not frame:
            return 'No symbol "' + self.arg + '" in current context.'
        try:
            eval(self.arg, frame.f_globals, frame.f_locals)
        except:
            return 'No symbol "' + self.arg + '" in current context.'
        s = "%d: %s" % (self.number,
                        fns.print_obj(self.arg, frame, self.fmt, True))
        return s

    def checkValid(self, frame):
        # Check if valid for this frame, and if not, delete display
        # To be used by code that creates a displayNode and only then.
        res = self.displayMe(frame)
        if res.split()[0] == 'No':
            self.deleteMe()
            # reset counter
            super.next -= 1
            pass
        return res

    def params(self):
        #print format and item to display
        pad = ' ' * (3 - len(`self.number`))
        if self.enabled:
           what = ' y  '
        else:
           what = ' n  '
           pass
        if self.fmt:
           what = what + self.fmt + ' '
        what = pad + what + self.arg
        print '%d:%s' % (self.number, what)
        return

    def deleteMe(self):
        self.list.remove(self)
        return

    def disableMe(self):
        self.enabled = False
        return

    def enableMe(self):
        self.enabled = True
        return
    pass

if __name__=='__main__':
    mgr = Display()
    import inspect
    x = 1
    frame = inspect.currentframe()
#     mgr.add(frame, 'x > 1')
#     for line in mgr.all(): print line
#     mgr.enable_disable(1, False)
#     for line in mgr.all(): print line
#     print mgr.display(frame)
#     mgr.enable_disable(1, False)
#     for line in mgr.display(frame): print line
#     mgr.enable_disable(1, True)
#     for line in mgr.display(frame): print line
#     mgr.clear()
#     print '-' * 10
#     for line in mgr.all(): print line
#     pass
