# -*- coding: utf-8 -*-
"""Classes to support gdb-like display/undisplay for pydb, the Extended
Python debugger. Class Display and DisplayNode are defined.

$Id: display.py,v 1.4 2007/01/08 12:09:19 rockyb Exp $"""

import fns

class Display:
    displayNext = 1
    displayList = []

    def displayIndex(self, frame):
        if not frame:
            return None
        # return suitable index for displayList
        code = frame.f_code
        return (code.co_name, code.co_filename, code.co_firstlineno)

    def displayAny(self, frame):
        # display any items that are active
        if not frame:
            return
        index = self.displayIndex(frame)
        for dp in Display.displayList:
            if dp.code == index and dp.enabled:
                print dp.displayMe(frame)

    def displayAll(self):
        """List all display items; return 0 if none"""
        any = 0
        for dp in Display.displayList:
            if not any:
                print """Auto-display expressions now in effect:
Num Enb Expression"""
                any = 1
            dp.params()
        return any

    def deleteOne(self, i):
        """Delete display expression i"""
        for dp in Display.displayList:
            if i == dp.number:
                dp.deleteMe()
                return

    def deleteAll(self):
        """Delete all display expressions"""
        for dp in Display.displayList:
            dp.deleteMe()
            return

    def enable(self, i, flag):
        for dp in Display.displayList:
            if i == dp.number:
                if flag:
                   dp.enableMe()
                else:
                   dp.disableMe()
                return

class DisplayNode(Display):

    def __init__(self, frame, arg, format):
        self.code = self.displayIndex(frame)
        self.format = format
        self.arg = arg
        self.enabled = True
        self.number = Display.displayNext
        Display.displayNext = Display.displayNext + 1
        Display.displayList.append(self)

    def displayMe(self, frame):
        if not frame:
            return 'No symbol "' + self.arg + '" in current context.'
        try:
            eval(self.arg, frame.f_globals, frame.f_locals)
        except:
            return 'No symbol "' + self.arg + '" in current context.'
        s = "%d: %s" % (self.number,
                        fns.print_obj(self.arg, frame, self.format, True))
        return s

    def checkValid(self, frame):
        # Check if valid for this frame, and if not, delete display
        # To be used by code that creates a displayNode and only then.
        res = self.displayMe(frame)
        if res.split()[0] == 'No':
            self.deleteMe()
            # reset counter
            Display.displayNext = Display.displayNext - 1
        return res

    def params(self):
        #print format and item to display
        pad = ' ' * (3 - len(`self.number`))
        if self.enabled:
           what = ' y  '
        else:
           what = ' n  '
        if self.format:
           what = what + self.format + ' '
        what = pad + what + self.arg
        print '%d:%s' % (self.number, what)

    def deleteMe(self):
        Display.displayList.remove(self)

    def disableMe(self):
        self.enabled = False

    def enableMe(self):
        self.enabled = True

