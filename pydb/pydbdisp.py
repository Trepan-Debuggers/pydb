"""$Id: pydbdisp.py,v 1.2 2006/02/24 18:58:51 rockyb Exp $
Classes to support display/undisplay for pydb, the Extended Python
debugger"""

class Display:
    displayNext = 1
    displayList = []

    def __init__(self):
        pass

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
                   dp.enable()
                else:
                   dp.disable()
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
            val = eval(self.arg, frame.f_globals, frame.f_locals)
        except:
            return 'No symbol "' + self.arg + '" in current context.'
        #format and print
        what = self.arg
        if self.format:
            what = self.format + ' ' + self.arg
            val = self.printf(val, self.format)
        return '%d: %s = %s' % (self.number, what, val)

    pconvert = {'c':chr, 'x': hex, 'o': oct, 'f': float, 's': str}
    twos = ('0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111',
            '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111')

    def printf(self, val, fmt):
        if not fmt:
            fmt = ' ' # not 't' nor in pconvert
        # Strip leading '/'
        if fmt[0] == '/':
            fmt = fmt[1:]
        f = fmt[0]
        if f in self.pconvert.keys():
            try:
                return apply(self.pconvert[f], (val,))
            except:
                return str(val)
        # binary (t is from 'twos')
        if f == 't':
            try:
                res = ''
                while val:
                    res = self.twos[val & 0xf] + res
                    val = val >> 4
                return res
            except:
                return str(val)
        return str(val)
        
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

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

