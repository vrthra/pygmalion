import induce.bc as bc
red = bc.bc(bc.bc.red)
class Grammar:
    def __init__(self, d={}): self._dict = d
    def __setitem__(self, key, item): self._dict[key] = item
    def __getitem__(self, key): return self.get(key)
    def get(self, key): return self._dict[key] if key in self._dict else set()
    def __bool__(self): return self._dict != {}
    def keys(self): return list(self._dict.keys())
    def values(self): return self._dict.values()
    def items(self): return self._dict.items()
    def __delitem__(self, key): del self._dict[key]
    def __missing__(self, key): return set()
    def get_dict(self):
        return {str(k):v for k,v in self._dict.items()}

    def reconstitute(self):
        def djs_to_string(djs):
            return "\n\t| ".join([i.inputval(self).replace('\n', '\n|\t')
                for i in sorted(djs)])
        def fixline(key, rules):
            fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
            return fmt % (key, djs_to_string(rules))
        return "\n".join([fixline(key, self[key]) for key in self.keys()])

    def __str__(self):
        def djs_to_string(djs):
            return "\n\t| ".join([str(i).replace('\n', '\n|\t')
                for i in sorted(djs)])
        def fixline(key, rules):
            fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
            return fmt % (key, djs_to_string(rules))
        return "\n".join([fixline(key, self[key]) for key in self.keys()])

    def compress(self):
        for i in self.keys():
            values = self.get(i)
            newvalues = set()
            addv = []
            last = None
            append = None
            for v in values:
                if len(v) == 1:
                    addv.append(v)
                else:
                    newvalues.add(v)
            if addv:
                newvalues.add(red('[') + ''.join(addv) + red(']'))
            self[i] = newvalues
        return self

class V:
    def __init__(self, fn, l, n, var, t, height=0):
        self.fn, self.l, self.func, self.var, self.t, self.height = fn, l, n, var, t, height
        self._x = (self.func, self.var, self.t)
    def __str__(self): return "<%s:%s:%d>" % self._x
    def __repr__(self): return "<%s:%s:%d>" % self._x
    def __hash__(self): return hash(self._x)
    def __eq__(self, other): return not (self != other)
    def __ne__(self, other): return self._x != other._x
