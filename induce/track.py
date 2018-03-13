import pudb; brk = pudb.set_trace
import pickle
from . import tstr
from . import grammar as g
from . import config

class Vars:
    def __init__(self, i, istack):
        self.i = i
        self.defs = {g.V(0, '', '', 'START', 0):i}
        self.accessed_scop_var = {}
        self.istack = istack

    def var_init(self, var):
        if var not in self.accessed_scop_var:
            self.accessed_scop_var[var] = 0

    def var_assign(self, var):
        self.accessed_scop_var[var] += 1

    def base_name(self, var, frame):
        return "%s:%s" % (frame['f_context'], var)

    def var_name(self, var, frame):
        # if we access the same variable at the same line number,
        # it is because it is a new scope.
        bv = self.base_name(var, frame)
        t = self.accessed_scop_var[bv]
        # DONT use line number. We are called from every line and the line
        # number is the line where a var is used  not where it is defined.
        return g.V(frame['f_code']['co_filename'], frame['f_lineno'],
                   frame['f_context'], var, t, self.istack.height())

    def update_vars(self, var, value, frame):
        # We can not detect variable reuse in different lines
        # however, we may be able to detect variable reuse
        # due to loops. The idea is that, when a variable gets
        # a changed value in terms of the *taint* (he_ll_o)
        # it means a new scope.
        tv = tstr.get_t(value)
        if not tv or len(tv) == 0 or not self.istack.has(tv): return
        bv = self.base_name(var, frame)
        self.var_init(bv)
        qual_var = self.var_name(var, frame)
        if qual_var not in self.defs:
            v = tstr.get_t(value)
            assert type(v) is tstr.tstr
            self.defs[qual_var] = v
        else: # possible reassignment
            oldv = self.defs[qual_var]
            newv = tstr.get_t(value)
            if oldv._taint != newv._taint:
                # only update the assignment if we detect a change
                # in taint value.
                self.var_assign(bv)
                qual_var = self.var_name(var, frame)
                self.defs[qual_var] = newv

def taint_include(gword, gsentence):
    return set(gword._taint) <= set(gsentence._taint)

class InputStack:
    def __init__(self):
        self.inputs = []

    def has(self, val):
        # TODO: Alternatively look only if val is tainted.
        # The idea is that any tainted value obviously comes
        # from the input
        return any(taint_include(val, var)
                for var in self.inputs[-1].values())

    def height(self):
        return len(self.inputs)

    def push(self, inputs):
        my_inputs = {k:tstr.get_t(v) for k,v in inputs.items() if tstr.get_t(v)}
        if self.inputs:
            my_inputs = {k:v for k,v in my_inputs.items() if self.has(v)}
        self.inputs.append(my_inputs)

    def pop(self): return self.inputs.pop()

    def __repr__(self):
        return repr(self.inputs)

class FrameIter:
    def __init__(self, fname):
        self.f = open(fname, 'rb')

    def __iter__(self): return self

    def __next__(self):
        try: return pickle.load(self.f)
        except EOFError:
            self.f.close()
            raise StopIteration

class Tracker:
    def __init__(self, i):
        self.istack = InputStack()
        self.vars = Vars(i, self.istack)


    # We record all string variables and values occurring during execution
    def track(self, o):
        event = o['event']
        if 'tstr.py' in o['loc'][0]: return
        frame = o['frame']
        f_code = frame['f_code']
        variables = frame['f_locals']
        funct = frame['f_context']
        if config.Ignore_Lambda and '<lambda>' in funct: return
        param_names = f_code['co_varnames'][0: f_code['co_argcount']]
        my_parameters = {k: variables[k] for k in param_names}
        if event == 'call':
            self.istack.push(my_parameters)

            if config.Track_Params:
                for var in my_parameters:
                    self.vars.update_vars(var, my_parameters[var], frame)
            return

        elif event == 'return':
            self.istack.pop()
            if config.Track_Return:
                var = '(<-' + funct + ')'
                self.vars.update_vars(var, o['arg'], frame['f_back'])
            return

        if config.Track_Vars:
            for var in variables:
                if not config.Track_Params:
                    if var in my_parameters: continue
                self.vars.update_vars(var, variables[var], frame)

