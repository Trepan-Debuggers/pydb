"""Functions to support the Extended Python Debugger.
$Id: fns.py,v 1.60 2009/03/20 01:30:51 rockyb Exp $"""
# -*- coding: utf-8 -*-
#   Copyright (C) 2007, 2008, 2009 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.

import dis, inspect, linecache, os, shlex, sys, re, traceback, types
from opcode import opname

# A pattern for a def header seems to be used a couple of times.
_re_def_str = r'^\s*def\s'
_re_def = re.compile(_re_def_str)

# arg_split culled from ipython's routine
def arg_split(s,posix=False):
    """Split a command line's arguments in a shell-like manner.

    This is a modified version of the standard library's shlex.split()
    function, but with a default of posix=False for splitting, so that quotes
    in inputs are respected."""
    
    lex = shlex.shlex(s, posix=posix)
    lex.whitespace_split = True
    return list(lex)

def checkline(obj, filename, lineno):
    """Check whether specified line seems to be executable.

    Return LINENO if it is, 0 if not (e.g. a docstring, comment, blank
    line or EOF). Warning: testing is not comprehensive.
    """
    if (2 == linecache.getline.func_code.co_argcount or not obj.curframe):
        line = linecache.getline(filename, lineno)
    else:
        line = linecache.getline(filename, lineno, obj.curframe.f_globals)
        pass
    if not line:
        obj.errmsg('End of file')
        return 0
    line = line.strip()
    # Don't allow setting breakpoint at a blank line
    if (not line or (line[0] == '#') or
         (line[:3] == '"""') or line[:3] == "'''"):
        obj.errmsg('Blank, doc string, or comment')
        return 0
    return lineno

def columnize_array(list, max_elts=50, displaywidth=80):
    """Display an array as a compact column-aligned set of columns.

    Columns are separated by two spaces (one was not legible enough).
    """
    if not list:
        return "<empty>\n"

    if len(list) > max_elts:
        list = list[0:max_elts-1]
        elipsis = True
    else:
        elipsis = False
    nonscalars = [i for i in range(len(list))
                  if not (type(list[i]) in [types.BooleanType, types.FloatType, 
                                            types.IntType,  types.StringType,
                                            types.UnicodeType, types.NoneType,
                                            types.LongType])]
    if nonscalars:
        return ("list[i] not a scalar for i in %s" %
                ", ".join(map(str, nonscalars)))
    size = len(list)
    if size == 1:
        return '[%s]' % str(list[0])
    # Consider arranging list in 1 rows total, then 2 rows...
    # Stop when at the smallest number of rows which
    # can be arranged less than the display width.
    for nrows in range(1, len(list)):
        ncols = (size+nrows-1) // nrows  # ceil(size/nrows)
        colwidths = []
        totwidth = -2
        # get max column width for this column
        for col in range(ncols):
            colwidth = 0
            for row in range(nrows):
                i = row*ncols + col # [rows, cols]
                if i >= size:
                    break
                x = list[i]
                colwidth = max(colwidth, len(repr(x)))
            colwidths.append(colwidth)
            totwidth += colwidth + 2
            if totwidth > displaywidth:
                break
        if totwidth <= displaywidth:
            break
    else:
        nrows = len(list)
        ncols = 1
        colwidths = [0]
    # The smallest number of rows computed and the
    # max widths for each column has been obtained.
    # Now we just have to format each of the
    # rows.
    s = '['
    for row in range(nrows):
        texts = []
        for col in range(ncols):
            i = row*ncols + col
            if i >= size:
                x = ""
            else:
                x = list[i]
            texts.append(x)
        while texts and not texts[-1]:
            del texts[-1]
        for col in range(len(texts)):
            texts[col] = repr(texts[col]).ljust(colwidths[col])
        s += ("%s\n "%str(", ".join(texts)))
    s = s[0:-2] 
    if elipsis: s += "..."
    s += ']'
    return s

def count_frames(frame, count_start=0):
    "Return a count of number of frames"
    count = -count_start
    while frame: 
        count += 1
        frame = frame.f_back
    return count

def decorate_fn_with_doc(new_fn, old_fn, additional_text=""):
    """Make new_fn have old_fn's doc string. This is particularly useful
    for the do_... commands that hook into the help system.
    Adapted from from a comp.lang.python posting
    by Duncan Booth."""
    def wrapper(*args, **kw):
        return new_fn(*args, **kw)
    wrapper.__doc__ = old_fn.__doc__ + additional_text
    return wrapper

def file_pyc2py(filename):
    """Given a file name, if the suffix is pyo or pyc (an optimized bytecode
    file), change that to the py equivalent"""
    if (filename.endswith(".pyc") or
        filename.endswith(".pyo")):
        return filename[:-1]
    return filename

def file2module(filename):
    """Given a file name, extract the most likely module name. """
    basename = os.path.basename(filename)
    if '.' in basename:
         pos = basename.rfind('.')
         return basename[:pos]
    else:
         return basename
    return None

def find_function(funcname, filename):
    try:
        cre = re.compile(r'def\s+%s\s*[(]' % re.escape(funcname))
        # cre = re.compile(r'%s\s*%s\s*[(]' % (_re_def_str, funcname))
    except:
        return None
    try:
        fp = open(filename)
    except IOError:
        return None
    # consumer of this info expects the first line to be 1
    lineno = 1
    answer = None
    while True:
        line = fp.readline()
        if line == '':
            break
        if cre.match(line):
            answer = funcname, filename, lineno
            break
        lineno += 1
    fp.close()
    return answer

def get_confirmation(obj, prompt, default=False):
    """ Called when a dangerous action is about to be done to make
    sure it's okay. Get a yes/no answer to `prompt' which is printed,
    suffixed with a question mark and the default value.  The user
    response converted to a boolean is returned.
    
    obj is an object that has a boolean `noninteractive' attribute and a
    `msg' method. The default value is used for the return if we aren't
    interactive.
    """
    if default:
        prompt += '? (Y or n) '
    else:
        prompt += '? (N or y) '
        pass
    while True and not obj.noninteractive:
        try:
            reply = raw_input(prompt).strip()
            reply = reply.strip().lower()
        except EOFError:
            reply = 'no'
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

def is_exec_stmt(frame):
    """Return True if we are looking at an exec statement"""
    return frame.f_back is not None and op_at_frame(frame.f_back)=='EXEC_STMT'

def get_call_function_name(frame):
    """If f_back is looking at a call function, return 
    the name for it. Otherwise return None"""
    f_back = frame.f_back
    if not f_back: return None
    if 'CALL_FUNCTION' != op_at_frame(f_back): return None

    co         = f_back.f_code
    code       = co.co_code
    labels     = dis.findlabels(code)
    linestarts = dict(dis.findlinestarts(co))
    inst       = f_back.f_lasti
    while inst >= 0:
        c = code[inst]
        op = ord(c)
        if inst in linestarts:
            inst += 1
            oparg = ord(code[inst]) + (ord(code[inst+1]) << 8)
            return co.co_names[oparg]
        inst -= 1
        pass
    return None

def get_last_tb_or_frame_tb():

    """Intended to be used going into post mortem routines.  If
    sys.last_traceback is set, we will return that and assume that
    this is what post-mortem will want. If sys.last_traceback has not
    been set, then perhaps we *about* to raise an error and are
    fielding an exception. So assume that sys.exc_info()[2]
    is where we want to look."""

    tb = sys.exc_info()[2]

    try:
        if inspect.istraceback(sys.last_traceback):
            # We do have a traceback so prefer that.
            tb = sys.last_traceback
    except AttributeError:
        pass
    return tb

def get_brkpt_lineno(obj, arg):
    """get_brkpt_lineno(obj,arg)->(filename, file, lineno)
    
    See if arg is a line number or a function name.  Return what
    we've found. None can be returned as a value in the triple.

    obj should be some sort of Gdb object and contain a curframe,
    errmsg and lineinfo method.
    """
    funcname, filename = (None, None)
    try:
        # First see if the breakpoint is an integer
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

def print_argspec(obj, obj_name):
    '''A slightly decorated version of inspect.format_argspec'''
    try:
        return obj_name + inspect.formatargspec(*inspect.getargspec(obj))
    except:
        return None
    return # Not reached

def print_obj(arg, frame, format=None, short=False):
    """Return a string representation of an object """
    try:
        if not frame:
            # ?? Should we have set up a dummy globals
            # to have persistence? 
            obj = eval(arg, None, None)
        else:
            obj = eval(arg, frame.f_globals, frame.f_locals)
    except:
        return 'No symbol "' + arg + '" in current context.'
    #format and print
    what = arg
    if format:
        what = format + ' ' + arg
        obj = printf(val, format)
    s = '%s = %s' % (what, obj)
    if not short:
        s += '\ntype = %s' % type(obj)
        if callable(obj):
            argspec = print_argspec(obj, arg)
            if argspec: 
                s += ':\n\t'
                if inspect.isclass(obj):
                    s += 'Class constructor information:\n\t'
                    obj = obj.__init__
                elif type(obj) is types.InstanceType:
                    obj = obj.__call__
                    pass
                s+= argspec
            pass

        # Try to list the members of a class.
        # Not sure if this is correct or the
        # best way to do.
        s = print_dict(s, obj, "object variables")
        if hasattr(obj, "__class__"):
            s = print_dict(s, obj.__class__, "class variables")
            pass
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

def op_at_frame(frame, pos=None):
    code = frame.f_code.co_code
    if pos is None: pos = frame.f_lasti
    try:
        op = ord(code[pos])
    except IndexError:
        return 'got IndexError'
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
    return

def runhooks(obj, hook_list, *args):
    for hook in hook_list:
        try: 
            hook(obj, args)
        except:
            pass
        return

def search_python_file(filename, directories=sys.path, 
                       module_globals=None):
    fullname = filename
    try:
        stat = os.stat(fullname)
    except os.error, msg:
        basename = os.path.split(filename)[1]

        # Try for a __loader__, if available
        if module_globals and '__loader__' in module_globals:
            name = module_globals.get('__name__')
            loader = module_globals['__loader__']
            get_source = getattr(loader, 'get_source', None)

            if name and get_source:
                if basename.startswith(name.split('.')[-1]+'.'):
                    try:
                        data = get_source(name)
                    except (ImportError, IOError):
                        pass
                    else:
                        if data is None:
                            # No luck, the PEP302 loader cannot find the source
                            # for this module.
                            return []
                        cache[filename] = (
                            len(data), None,
                            [line+'\n' for line in data.splitlines()], fullname
                        )
                        return cache[filename][2]

        # Try looking through the module search path, taking care to handle packages.

        if basename == '__init__.py':
            # filename referes to a package
            basename = filename

        for dirname in sys.path:
            # When using imputil, sys.path may contain things other than
            # strings; ignore them when it happens.
            try:
                fullname = os.path.join(dirname, basename)
            except (TypeError, AttributeError):
                # Not sufficiently string-like to do anything useful with.
                pass
            else:
                try:
                    stat = os.stat(fullname)
                    break
                except os.error:
                    pass
        else:
            # No luck
##          print '*** Cannot stat', filename, ':', msg
            return []
    try:
        fp = open(fullname, 'rU')
        lines = fp.readlines()
        fp.close()
    except IOError, msg:
##      print '*** Cannot open', fullname, ':', msg
        return []


def search_file(filename, directories, cdir):
    """Return a full pathname for filename if we can find one. path
    is a list of directories to prepend to filename. If no file is
    found we'll return None"""

    for trydir in directories:

        # Handle $cwd and $cdir
        if trydir =='$cwd': trydir='.'
        elif trydir == '$cdir': trydir = cdir

        tryfile = os.path.abspath(os.path.join(trydir, filename))
        if os.path.isfile(tryfile):
            return tryfile
    return None
    
def show_onoff(bool):
    """Return 'on' for True and 'off' for False, and ?? for anything
    else."""
    if type(bool) != types.BooleanType:
        return "??"
    if bool:
        return "on"
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

def whence_file(py_script):
    """Do a shell-like path lookup for py_script and return the results.
    If we can't find anything return py_script"""
    if py_script.find(os.sep) != -1:
        # Don't search since this name has path separator components
        return py_script
    for dirname in os.environ['PATH'].split(os.pathsep):
        py_script_try = os.path.join(dirname, py_script)
        if os.path.exists(py_script_try):
            return py_script_try
    # Failure
    return py_script

if __name__ == '__main__':
    print "show_onoff(True is %s)" % str(show_onoff(True))
    assert show_onoff(True) == 'on'
    print "show_onoff(False is %s)" % str(show_onoff(False))
    print print_argspec(show_onoff, 'show_onoff')
    assert show_onoff(False) == 'off'
    print "search_file('fns.py', '.', '.'): %s" % (
        search_file("fns.py", ["$cwd", "$cdir"], "."))
    assert printf(31, "/o") == '037'
    assert printf(31, "/t") == '00011111'
    assert printf(33, "/c") == '!'
    assert printf(33, "/x") == '0x21'
    assert file2module("/tmp/gcd.py") == 'gcd'

    assert columnize_array(["a"]) == "[a]"
    print columnize_array([
            "one", "two", "three",
            "4ne", "5wo", "6hree",
            "7ne", "8wo", "9hree",
            "10e", "11o", "12ree",
            "13e", "14o", "15ree",
            "16e", "17o", "18ree",
            "19e", "20o", "21ree",
            "22e", "23o", "24ree",
            "25e", "26o", "27ree",
            "28e", "29o", "30ree",
            "31e", "32o", "33ree",
            "34e", "35o", "36ree",
            "37e", "38o", "39ree",
            "40e", "41o", "42ree",
            "43e", "44o", "45ree",
            "46e", "47o", "48ree",
            "one", "two", "three"])
    pass

