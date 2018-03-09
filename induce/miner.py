#!/usr/bin/env python3
# Mine a grammar from dynamic behavior
import pudb; brk = pudb.set_trace
from . import grammar as g

class NTKey:
    def __init__(self, k):
        assert type(k) is g.V
        self.k = k
    def __repr__(self): return "$%s" % self.k
    def __str__(self): return "$%s" % self.k

class Rule:
    def __init__(self,k, v):
        self.k = k
        self.v = v
        self._taint = v._taint
        self._rindex = {tainted_range(self): v}

    def ranges(self): return sorted(self._rindex, key=lambda a: a.start)
    def __lt__(self, o): return str(self).__lt__(str(o))
    def __repr__(self): return 'Rule[%s]:=%s' % (self.k, self.value())
    def value(self): return ''.join(str(self._rindex[k]) for k in self.ranges())

    def cur_taint(self):
        t = [-1] * len(self.taint)
        for k in self.ranges():
            v = self._rindex[k]
            if hasattr(v, '_taint'): t[k.start:k.stop] = v._taint[:]
        return t

    def _tinclude(self, o):
        return next((k for k in self._rindex if set(o._taint) <= set(k)), None)

    def _encloses(self, o):
        return self.taint[0] <= o._taint[0] and self.taint[-1] >= o._taint[-1]

    @property
    def taint(self): return self._taint

    def keys_enclosed_by(self, largerange):
        # keys enclosed by the given range within this rule.
        l = [k for k in self.ranges() if k.start in largerange]
        assert all(k.stop - 1 in largerange for k in l)
        return l

    def include(self, word):
        if not self._encloses(word): return False
        # When we paste the taints of new word in, (not replace)
        # then, does it get us more coverage? (i.e more -1s)
        ct = self.cur_taint()
        cur_tsum = sum(i for i in ct if i < 0)
        ts = self.taint[:] # the original taint
        start_i, stop_i = ts.index(word._taint[0]), ts.index(word._taint[-1])
        ct[start_i:stop_i+1] = [-1] * len(word)
        new_sum = sum(i for i in ct if i < 0)
        if new_sum < cur_tsum: return True
        return False

    def _replace_tainted_str(self, o, ntkey):
        trange = tainted_range(o)
        keytaint = self._tinclude(o)
        # get starting point.
        my_str = self._rindex[keytaint]
        if type(my_str) is not NTKey:
            del self._rindex[keytaint]
            splitA = trange.start - keytaint.start
            init_range = range(keytaint.start, trange.start)
            mid_range = range(trange.start, trange.stop)
            end_range = range(trange.stop, keytaint.stop)
            if init_range: self._rindex[init_range] = my_str[0:splitA]
            self._rindex[mid_range] = ntkey
            if end_range: self._rindex[end_range] = my_str[splitA + len(o):]
            return []
        else:
            pass
            # TODO

    def replace_with_key(self, o, ntkey):
        # we need to handle these
        # s = peek(1)
        # if s == 't': read_str('true')
        # or
        # i = read_num(), point = read('.'), d = read_num()
        # number = i + point + d
        trange = tainted_range(o)
        keytaint = self._tinclude(o)
        if not keytaint:
            # the complete taint range is not contained, but we are still
            # inclued in the original. It means that an inbetween variable has
            # obscured our inclusion.
            eclipsed = self.keys_enclosed_by(trange)
            # So we need to take these eclipsed variables and remove from
            # this rule after setting this var instead.
            evalues = {k:self._rindex[k] for k in eclipsed
                    if type(self._rindex[k]) is NTKey} # choose only keys
            for k in eclipsed: del self._rindex[k]
            self._rindex[trange] = ntkey
            return evalues
        else:
            return self._replace_tainted_str(o, ntkey)

    def update_with_key(self, o, ntkey, my_grammar):
        trange = tainted_range(o)
        keytaint = self._tinclude(o)
        if not keytaint:
            assert False
        else:
            my_str = self._rindex[keytaint]
            # we are replacing part of another (larger) key
            # so, get its corresponding rule, and replace it there.
            if type(my_str) is NTKey:
                rule = my_grammar[my_str]
                # update the value o with key key
                # check if the rule is smaller
                if len(rule.v) > len(o):
                    rule.update_with_key(o, ntkey, my_grammar)
                else:
                    assert False
            else:
                self._replace_tainted_str(o, ntkey)


def tainted_range(o): return range(o._taint[0], o._taint[-1]+1)

# Obtain a grammar for a specific input
def get_grammar(assignments):
    my_grammar = {}
    # all values are tainted strings.
    for var, value in assignments.items():
        all_eclipsed = []
        nt_var = NTKey(var)
        append = False if my_grammar else True
        for key, rule in my_grammar.items():
            if rule.include(value):
                eclipsed = rule.replace_with_key(value, nt_var)
                # eclipsed are the keys displaced from rule by value
                # and needs to be added to value.
                if eclipsed:
                    all_eclipsed.append((eclipsed, nt_var))
            append = True

        # Until merge, all keys have a single rule.
        if append: my_grammar[nt_var] = Rule(nt_var, value)

        for einfo in all_eclipsed:
            eclipsed, by_var_key = einfo
            rule = my_grammar[by_var_key]
            for ek in eclipsed:
                ev = eclipsed[ek]
                r = my_grammar[ev]
                x = rule.update_with_key(r.v, r.k, my_grammar)
                assert not x # if not empty, recurse

    return g.Grammar({k:{v} for k,v in my_grammar.items()})

def merge_grammars(g1, g2):
    return g.Grammar({str(key): g1[key] | g2[key] for key in g1.keys() + g2.keys()})

# Get a grammar for multiple inputs
def infer_grammar(traces):
    merged_grammar = g.Grammar()
    for instr, defs in traces:
        grammar = get_grammar(defs)
        # print(repr(instr) + " ->\n" + str(grammar))
        merged_grammar = merge_grammars(merged_grammar, grammar)
    return merged_grammar

