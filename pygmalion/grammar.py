import string
import pygmalion.config as config
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

class V:
    def __init__(self, fn, l, n, var, t, height=0):
        self.fn, self.l, self.func, self.var, self.t, self.height = fn, l, n, var, str(t), height
        self._x = (self.func, self.var, str(self.t))
    def newV(self, t):
        return V(self.fn, self.l, self.func, self.var, t, self.height)
    def __str__(self): return "<%s:%s:%s>" % self._x
    def __repr__(self): return "<%s:%s:%s>" % self._x
    def __hash__(self): return hash(self._x)
    def __eq__(self, other): return not (self != other)
    def __ne__(self, other): return self._x != other._x
    @classmethod
    def start(cls):
        return V(0, '', '', 'START', 0)

class Not:
    def __init__(self, v):
        self.v = v
    def __str__(self): return "[^%s]" % str(self.v.val())
    def __repr__(self): return "!%s" % str(self.v)
    def __bool__(self): return bool(self.v)

class Box:
    def __init__(self, v):
        self.v = v
    def val(self): return to_str(self.v)
    def __str__(self): return "[%s]" % self.val()
    def __repr__(self): return "<%s>" % ''.join(self.v)
    def __bool__(self): return len(''.join(self.v)) > 0

class Choice:
    def __init__(self, a, b):
        self.a, self.b = a, b
    def __repr__(self): return 'choice: %s' % str(self)
    def __str__(self):
        x = self.val()
        return simplify(x)
    def val(self):
        if self.a and not self.b:
            return str(self.a)
        elif not self.a and self.b:
            return str(self.b)
        else:
            if config.Simple_Class:
                return '%s' % self.a
            else:
                return '(%s&%s)' % (self.a, self.b)
    def __eq__(self, o):
        return type(o) == Choice and str(self) == str(o)


class NTKey:
    def __init__(self, k):
        assert type(k) is V
        self.k = k
    def __repr__(self): return "$%s" % self.k
    def __str__(self): return "$%s" % self.k
    def __hash__(self): return hash(self.k)
    def __eq__(self, o): return type(o) == NTKey and self.k == o.k
    def __ne__(self, o): return not (self == o)

class Rule:
    def __init__(self, k, rvalues, taint=None, comparisons=None):
        self.k = k
        self._rvalues = rvalues
        self._taint = taint
        self.comparisons = comparisons
    def rvalues(self): return self._rvalues
    def value(self): return ''.join(str(k) for k in self._rvalues)
    def __str__(self): return self.value()
    def __repr__(self):
        return 'Rule[%s]:=%s' % (self.k, self.value())
    def __hash__(self): return hash(self.value())
    def __eq__(self, o): return type(o) == Rule and self.value() == o.value()
    def __lt__(self, o): return str(self).__lt__(str(o))
    def __iter__(self): return iter(self.rvalues())
    def to_rwrap(self, rvals):
        return Rule(self.k, rvals, self._taint, self.comparisons)

def escape(v):
    return v

def simplify(x):
    x = x.replace('0123456789', '0-9')
    x = x.replace('abcdefghijklmnopqrstuvwxyz', 'a-z')
    x = x.replace('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'A-Z')
    return x

def to_str(k):
    v = ''
    if not k:
        return ':empty:'
    for i in k:
        if str(i) not in string.punctuation + string.digits + string.ascii_letters:
            v+= repr(i)[1:-1]
        else:
            v += i
    r = ''.join(sorted(v))
    r = r.replace('+-.', '-+.')
    return r

