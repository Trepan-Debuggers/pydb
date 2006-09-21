"""$Id: fns.py,v 1.24 2006/09/21 09:45:51 rockyb Exp $
Functions to support the Extended Python Debugger."""
import inspect, linecache, os, sys, re, traceback, types

# A pattern for a def header seems to be used a couple of times.
_re_def_str = r'^\s*def\s'
_re_def = re.compile(_re_def_str)
    
def checkline(obj, filename, lineno):
    """Check whether specified line seems to be executable.

    Return `lineno` if it is, 0 if not (e.g. a docstring, comment, blank
    line or EOF). Warning: testing is not comprehensive.
    """
    line = linecache.getline(filename, lineno)
    if not line:
        obj.errmsg('End of file')
        return 0
    line = line.strip()
    # Don't allow setting breakpoint at a blank line
    if (not line or (line[0] == '#') or
         (line[:3] == '"""') or line[:3] == "'''"):
        obj.errmsg('Blank or comment')
        return 0
    return lineno

def find_function(funcname, filename):
    cre = re.compile(r'def\s+%s\s*[(]' % funcname)
    # cre = re.compile(r'%s\s*%s\s*[(]' % (_re_def_str, funcname))
    try:
        fp = open(filename)
    except IOError:
        return None
    # consumer of this info expects the first line to be 1
    lineno = 1
    answer = None
    while 1:
        line = fp.readline()
        if line == '':
            break
        if cre.match(line):
            answer = funcname, filename, lineno
            break
        lineno = lineno + 1
    fp.close()
    return answer

def get_confirmation(obj, prompt, default=False):
    """Get a yes/no answer to prompt. obj is an object that has
    a boolean noninteractive attribute and a msg method. The default
    value is used for the return if we aren't interactive.
    """
    while True and not obj.noninteractive:
        try:
            reply = raw_input(prompt)
        except EOFError:
            reply = 'no'
            reply = reply.strip().lower()
        if reply in ('y', 'yes'):
            return True
        elif reply in ('n', 'no'):
            return False
        else:
            obj.msg("Please answer y or n.")
    return default
                

def get_exec_string(frame, max=30):
    """get_exec_string(frame, max)->prefix string Get
    the initial part the string in an exec command.  frame is the
    frame, and max characters of the string will be returned adjusted
    with a trailing ... and any quote mark.  A real hack until
    tracebacks do better in location reporting. """
    
    if frame == None: return None
    fi, li, fn, text = traceback.extract_stack(frame)[-1]
    re_exec = re.compile(r'(^|\s+)exec\s+(.*)')
    mo = re_exec.search(text)
    if mo:
        exec_arg = mo.group(2)
        if len(exec_arg) > max:
            if exec_arg[0] == '"' or \
                   exec_arg[0] == "'":
                quote=exec_arg[0]
            else:
                quote=''
                return "%s...%s" % (exec_arg[0:max], quote)
        else:
            return exec_arg
    return None

def is_def_stmt(line, frame):
    """Return True if we are looking at a def statement"""
    # Should really also check that operand is a code object
    return _re_def.match(line) and op_at_frame(frame)=='LOAD_CONST'

def is_exec_stmt(frame):
    """Return True if we are looking at an exec statement"""
    return frame.f_back is not None and op_at_frame(frame.f_back)=='EXEC_STMT'

def get_last_tb_or_frame_tb(frameno=1):

    """Intended to be used going into post mortem routines.  If
    sys.last_traceback is set, we will return that and assume that
    this is what post-mortem will want. If sys.last_traceback has not
    been set, then perhaps we *about* to raise an error and are
    fielding an exception. So assume that sys.exec_info()[frameno]
    is where we want to look."""

    traceback = sys.exc_info()[frameno]

    try:
        if inspect.istraceback(sys.last_traceback):
            # We do have a traceback so prefer that.
            traceback = sys.last_traceback
    except AttributeError:
        pass
    return traceback

def print_dict(s, obj, title):
    if hasattr(obj, "__dict__"):
        d=obj.__dict__
        if type(d) == types.DictType or type(d) == types.DictProxyType:
            s += "\n%s:\n" % title
            keys = d.keys()
            keys.sort()
            for key in keys:
                s+="  '%s':\t%s\n" % (key, d[key])
    return s

def print_obj(arg, frame, format=None, short=False):
    """Return a string representation of an object """
    try:
        if not frame:
            # ?? Should we have set up a dummy globals
            # to have persistence? 
            val = eval(arg, None, None)
        else:
            val = eval(arg, frame.f_globals, frame.f_locals)
    except:
        return 'No symbol "' + arg + '" in current context.'
    #format and print
    what = arg
    if format:
        what = format + ' ' + arg
        val = printf(val, format)
    s = '%s = %s' % (what, val)
    if not short:
        s += '\ntype = %s' % type(val)
        # Try to list the members of a class.
        # Not sure if this is correct or the
        # best way to do.
        s = print_dict(s, val, "object variables")
        if hasattr(val, "__class__"):
            s = print_dict(s, val.__class__, "class variables")
    return s

pconvert = {'c':chr, 'x': hex, 'o': oct, 'f': float, 's': str}
twos = ('0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111',
        '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111')

def printf(val, fmt):
    global pconvert, twos
    if not fmt:
        fmt = ' ' # not 't' nor in pconvert
    # Strip leading '/'
    if fmt[0] == '/':
        fmt = fmt[1:]
    f = fmt[0]
    if f in pconvert.keys():
        try:
            return apply(pconvert[f], (val,))
        except:
            return str(val)
    # binary (t is from 'twos')
    if f == 't':
        try:
            res = ''
            while val:
                res = twos[val & 0xf] + res
                val = val >> 4
            return res
        except:
            return str(val)
    return str(val)


from opcode import opname
def op_at_frame(frame, pos=None):
    code = frame.f_code.co_code
    if pos is None: pos = frame.f_lasti
    op = ord(code[pos])
    # print "+++ %s" % opname[op]
    return opname[op]

def print_stack_entry(obj, i_stack):
    frame_lineno = obj.stack[len(obj.stack)-i_stack-1]
    frame, lineno = frame_lineno
    if frame is obj.curframe:
        obj.msg_nocr('->')
    else:
        obj.msg_nocr('##')
    obj.msg("%d %s" %
             (i_stack, obj.format_stack_entry(frame_lineno)))

def print_stack_trace(obj, count=None):
    "Print count entries of the stack trace"
    if count is None:
        n=len(obj.stack)
    else:
        n=min(len(obj.stack), count)
    try:
        for i in range(n):
            print_stack_entry(obj, i)
    except KeyboardInterrupt:
        pass

def search_file(filename, path, cdir):
    """Return a full pathname for filename if we can find one. path
    is a list of directories to prepend to filename. If no file is
    found we'll return filename"""

    dirs=path.split(":")
    for trydir in dirs:

        # Handle $cwd and $cdir
        if trydir =='$cwd': trydir='.'
        elif trydir == '$cdir': trydir = cdir

        tryfile = os.path.abspath(os.path.join(trydir, filename))
        if os.path.isfile(tryfile):
            return tryfile
    
def show_onoff(bool):
    """Return 'on' for True and 'off' for False, and ?? for anything
    else."""
    if type(bool) != types.BooleanType:
        return "??"
    if bool:
        return "on"
    else:
        return "off"

def parse_filepos(obj, arg):
    """parse_filepos(obj, arg)->(fn, filename, lineno)
    
    Parse arg as [filename:]lineno | function
    Make sure it works for C:\foo\bar.py:12
    """
    colon = arg.rfind(':') 
    if colon >= 0:
        filename = arg[:colon].rstrip()
        f = obj.lookupmodule(filename)
        if not f:
            obj.errmsg("'%s' not found using sys.path" % filename)
            return (None, None, None)
        else:
            filename = f
            arg = arg[colon+1:].lstrip()
        try:
            lineno = int(arg)
        except TypeError:
            obj.errmsg("Bad lineno: %s", str(arg))
            return (None, filename, None)
        return (None, filename, lineno)
    else:
        # no colon: can be lineno or function
        return get_brkpt_lineno(obj, arg)

def get_brkpt_lineno(obj, arg):
    """get_brkpt_lineno(obj,arg)->(filename, file, lineno)
    
    See if arg is a line number or a function name.  Return what
    we've found. None can be returned as a value in the triple.

    obj should be some sort of Gdb object and contain a curframe,
    errmsg and lineinfo method.
    """
    funcname, filename = (None, None)
    try:
        # First see if the breakpont is an integer
        lineno = int(arg)
        filename = obj.curframe.f_code.co_filename
    except ValueError:
        try:
            func = eval(arg, obj.curframe.f_globals,
                        obj.curframe.f_locals)
        except:
            func = arg
        try:
            # See if agument is a function name
            if hasattr(func, 'im_func'):
                func = func.im_func
            code = func.func_code
            # use co_name to identify the bkpt (function names
            #could be aliased, but co_name is invariant)
            lineno = code.co_firstlineno
            filename = code.co_filename
        except:
            # The last possibility is that a breakpoint argument can be
            # is some sort of file + linenumber.
            (ok, filename, ln) = obj.lineinfo(arg)
            if not ok:
                obj.errmsg(('The specified object %s is not'
                            +' a function, or not found'
                            +' along sys.path or no line given.')
                           % str(repr(arg)))
                return (None, None, None)
            funcname = ok
            lineno = int(ln)
    return (funcname, filename, lineno)


if __name__ == '__main__':
    print "show_onoff(True is %s)" % str(show_onoff(True))
    assert show_onoff(True) == 'on'
    print "show_onoff(False is %s)" % str(show_onoff(False))
    assert show_onoff(False) == 'off'
    print "search_file('fns.py', '.', '.'): %s" % search_file("fns.py",
                                                              "$cwd:$cdir",
                                                              ".")
    assert printf(31, "/o") == '037'
    assert printf(31, "/t") == '00011111'
    assert printf(33, "/c") == '!'
    assert printf(33, "/x") == '0x21'

