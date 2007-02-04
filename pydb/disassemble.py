# Modified from dis. Changed output to use msg and msg_nocr.
# Added first_line and last_line parameters
import types
from dis import distb, findlabels, findlinestarts
from opcode import *

def dis(obj, x=None, start_line=-1, end_line=None):
    """Disassemble classes, methods, functions, or code.

    With no argument, disassemble the last traceback.

    """
    if x is None:
        distb()
        return
    if type(x) is types.InstanceType:
        x = x.__class__
    if hasattr(x, 'im_func'):
        x = x.im_func
    if hasattr(x, 'func_code'):
        x = x.func_code
    if hasattr(x, '__dict__'):
        items = x.__dict__.items()
        items.sort()
        for name, x1 in items:
            if type(x1) in (types.MethodType,
                            types.FunctionType,
                            types.CodeType,
                            types.ClassType):
                obj.msg("Disassembly of %s:" % name)
                try:
                    dis(obj, x1, start_line=start_line, end_line=end_line)
                except TypeError, msg:
                    obj.msg("Sorry:", msg)
                obj.msg("")
    elif hasattr(x, 'co_code'):
        disassemble(obj, x, start_line=start_line, end_line=end_line)
    elif isinstance(x, str):
        dis.disassemble_string(x)
    else:
       obj.errmsg("Don't know how to disassemble %s objects." % 
                  type(x).__name__)
    return

def disassemble(obj, co, lasti=-1, start_line=-1, end_line=None,
                ):
    """Disassemble a code object."""
    disassemble_string(obj, co.co_code, lasti, co.co_firstlineno,
                       start_line, end_line,
                       co.co_varnames, co.co_names, co.co_consts,
                       co.co_cellvars, co.co_freevars,
                       dict(findlinestarts(co)))
    return

def disassemble_string(obj, code, lasti=-1, cur_line=0,
                       start_line=-1, end_line=None,
                       varnames=(), names=(), consts=(), cellvars=(),
                       freevars=(), linestarts={}):
    """Disassemble byte string of code."""
    labels = findlabels(code)
    n = len(code)
    i = 0
    extended_arg = 0
    free = None
    null_print = lambda x: None
    if start_line > cur_line:
        msg_nocr = null_print
        msg = null_print
    else:
        msg_nocr = obj.msg_nocr
        msg = obj.msg
    while i < n:
        c = code[i]
        op = ord(c)
        if i in linestarts:
            if i > 0:
                msg("")
            cur_line = linestarts[i]
            if start_line and start_line > cur_line:
                msg_nocr = null_print
                msg = null_print
            else:
                msg_nocr = obj.msg_nocr
                msg = obj.msg
            if end_line and cur_line > end_line: break
            msg_nocr("%3d" % cur_line)
        else:
            msg_nocr('   ')

        if i == lasti: msg_nocr('-->')
        else: msg_nocr('   ')
        if i in labels: msg_nocr('>>')
        else: msg_nocr('  ')
        msg_nocr(repr(i).rjust(4))
        msg_nocr(opname[op].ljust(20))
        i = i+1
        if op >= HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
            extended_arg = 0
            i = i+2
            if op == EXTENDED_ARG:
                extended_arg = oparg*65536L
            msg_nocr(repr(oparg).rjust(5))
            if op in hasconst:
                msg_nocr('(' + repr(consts[oparg]) + ')')
            elif op in hasname:
                msg_nocr('(' + names[oparg] + ')')
            elif op in hasjrel:
                msg_nocr('(to ' + repr(i + oparg) + ')')
            elif op in haslocal:
                msg_nocr('(' + varnames[oparg] + ')')
            elif op in hascompare:
                msg_nocr('(' + cmp_op[oparg] + ')')
            elif op in hasfree:
                if free is None:
                    free = cellvars + freevars
                msg_nocr('(' + free[oparg] + ')')
        msg("")
    return

