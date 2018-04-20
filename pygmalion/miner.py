#!/usr/bin/env python3
# Mine the parse trees
import pudb; brk = pudb.set_trace
from . import grammar as g
from . import config


class Def:
    def __init__(self,k, v):
        self.k = k
        self.v = v
        self._taint = v._taint
        self._rindex = {tainted_range(self): v}
        self.comparisons = None

    def to_rwrap(self, rvals):
        return g.Rule(self.k, rvals, self._taint, self.comparisons)

    def ranges(self): return sorted(self._rindex, key=lambda a: a.start)
    def __lt__(self, o): return str(self).__lt__(str(o))
    def __repr__(self): return 'Def[%s]:=%s' % (self.k, self.value())
    def value(self): return ''.join(str(k) for k in self.rvalues())
    def rvalues(self): return [self._rindex[k] for k in self.ranges()]
    def __str__(self): return self.value()
    def __iter__(self): return iter(self.rvalues())

    def reconstitute(self, v, g):
        if type(v) is g.NTKey:
            # get the value from grammar
            val = list(g[v])
            assert len(val) == 1 # only for linear grammars
            return val[0].inputval(g)
        else:
            return str(v)

    def inputval(self, g): return ''.join([self.reconstitute(k,g) for k in self.rvalues()])

    def __hash__(self): return hash((self.k, self.v, tuple(self._taint),
        tuple((k,v) for k,v in self._rindex.items())))
    def __nq__(self, o):
        if self.k != o.k: return True
        if self.v != o.v: return True
        if self._taint != o._taint: return True
        if self._rindex != o._rindex: return True
        return False

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
        # assert all(k.stop - 1 in largerange for k in l)
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
        if new_sum <= cur_tsum: return True
        return False

    def _replace_tainted_str(self, o, ntkey):
        trange = tainted_range(o)
        keytaint = self._tinclude(o)
        # get starting point.
        my_str = self._rindex[keytaint]
        if type(my_str) is not g.NTKey:
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
            # we have two choices to make when there are
            # eclipsed keys. One is to skip this key
            # the other is to swap the relative positions of keys
            if not config.Swap_Eclipsing_Keys: return []
            # the complete taint range is not contained, but we are still
            # inclued in the original. It means that an inbetween variable has
            # obscured our inclusion.
            eclipsed = self.keys_enclosed_by(trange)
            # So we need to take these eclipsed variables and remove from
            # this rule after setting this var instead.
            evalues = {k:self._rindex[k] for k in eclipsed
                    if type(self._rindex[k]) is g.NTKey} # choose only keys
            for k in eclipsed: del self._rindex[k]
            self._rindex[trange] = ntkey
            return evalues
        else:
            return self._replace_tainted_str(o, ntkey)

    def update_with_key(self, o, ntkey, my_grammar):
        trange = tainted_range(o)
        keytaint = self._tinclude(o)
        if not keytaint:
            pass
            # TODO
        else:
            my_str = self._rindex[keytaint]
            # we are replacing part of another (larger) key
            # so, get its corresponding rule, and replace it there.
            if type(my_str) is g.NTKey:
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
def get_parse_tree(assignments):
    my_grammar = {}
    # all values are tainted strings.
    for var, value in assignments.items():
        all_eclipsed = []
        nt_var = g.NTKey(var)
        append = False if my_grammar else True
        for key, rule in my_grammar.items():
            # is the key at a higher stack height than var?
            # only replace things at a lower height with something
            # at higher height.
            # i.e key(rule).height should be smaller than var.height
            val = True
            if config.Prevent_Deep_Stack_Modification:
                val = key.k.height <= var.height
            if val and rule.include(value):
                # but we still need to let keys below in the stack be
                # eclipsed.
                eclipsed = rule.replace_with_key(value, nt_var)
                # eclipsed are the keys displaced from rule by value
                # and needs to be added to value.
                if eclipsed:
                    if not config.Strip_Peek:
                        all_eclipsed.append((eclipsed, nt_var))
                append = True

        # Until merge, all keys have a single definition.
        if append: my_grammar[nt_var] = Def(nt_var, value)

        for einfo in all_eclipsed:
            eclipsed, by_var_key = einfo
            rule = my_grammar[by_var_key]
            for ek in eclipsed:
                ev = eclipsed[ek]
                r = my_grammar[ev]
                x = rule.update_with_key(r.v, r.k, my_grammar)
                assert not x # if not empty, recurse

    # Use this instead if you want the grammar values to be isomorphic
    # only upto their string value.
    # return g.Grammar({k:{v.value()} for k,v in my_grammar.items()})
    return g.Grammar({k:{v} for k,v in my_grammar.items()})

# Get a grammar for multiple inputs
def mine_parse_tree(definitions):
    for (i, xins, defs) in definitions:
        yield (i, xins, get_parse_tree(defs))

