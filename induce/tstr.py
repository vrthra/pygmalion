import inspect
import enum

class Op(enum.Enum):
    LT = 0
    LE = enum.auto()
    EQ = enum.auto()
    NE = enum.auto()
    GT = enum.auto()
    GE = enum.auto()
    IN = enum.auto()
    NOT_IN = enum.auto()
    IS = enum.auto()
    IS_NOT = enum.auto()
    ISSUBCLASS = enum.auto()
    FIND_STR = enum.auto()
    SPLIT_STR = enum.auto()

COMPARE_OPERATORS = {
        Op.EQ: lambda x, y: x == y,
        Op.NE: lambda x, y: x != y,
        Op.IN: lambda x, y: x in y,
        Op.NOT_IN: lambda x, y: x not in y
        }

class Instr:
    def __init__(self,o, a, b):
        self.opA = a
        self.opB = b
        self.op = o

    def o(self):
        if self.op == Op.EQ:
            return 'eq'
        elif self.op == Op.NE:
            return 'ne'
        else:
            return '?'

    def __repr__(self):
        return "%s,%s,%s" % (self.o(), repr(self.opA), repr(self.opB))

    def __str__(self):
        if self.op == Op.EQ:
            if str(self.opA) == str(self.opB):
                return "%s = %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s != %s" %  (repr(self.opA), repr(self.opB))
        elif self.op == Op.NE:
            if str(self.opA) == str(self.opB):
                return "%s = %s" %  (repr(self.opA), repr(self.opB))
            else:
                return "%s != %s" %  (repr(self.opA), repr(self.opB))
        elif self.op == Op.IN:
            if str(self.opA) in str(self.opB):
                return "%s in %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s not in %s" %  (repr(self.opA), repr(self.opB))
        elif self.op == Op.NOT_IN:
            if str(self.opA) in str(self.opB):
                return "%s in %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s not in %s" %  (repr(self.opA), repr(self.opB))
        else:
            assert False

Comparisons = []
class tstr_iterator():
    def __init__(self, tstr):
        self._tstr = tstr
        self._str_idx = 0

    def __next__(self):
        if self._str_idx == len(self._tstr): raise StopIteration
        # calls tstr getitem should be tstr
        c = self._tstr[self._str_idx]
        assert type(c) is tstr
        self._str_idx += 1
        return c


class tstr(str):
    def __new__(cls, value, *args, **kw):
        return super(tstr, cls).__new__(cls, value)

    def __init__(self, value, taint=None, parent=None):
        # tain map contains non-overlapping portions that are mapped to the
        # original string
        self.parent = parent
        l = len(self)
        if taint:
            # assert that the provided tmap carries only
            # as many entries as len.
            assert len(taint) == len(self)
            self._taint = taint
        else:
            self._taint = list(range(0, len(self)))

    def __repr__(self):
        return str.__repr__(self) # + ':' + str((self._idx, self._unmapped_till))

    def __str__(self):
        return str.__str__(self)

    def x(self, i=0):
        v = self._x(i)
        if v < 0:
            raise Exception('Invalid mapped char idx in tstr')
        return v

    def _x(self, i=0):
        return self.get_mapped_char_idx(i)

    def get_mapped_char_idx(self, i):
        """
        >>> my_str = tstr('abc')
        >>> my_str.get_mapped_char_idx(0)
        0
        >>> my_str = tstr('abcdefghijkl', taint=list(range(4,16)))
        >>> my_str.get_mapped_char_idx(4)
        8
        """

        # if the current string is not mapped to input till
        # char 10 (_unmapped_till), but the
        # character 10 is mapped to character 5 (_idx)
        # then requesting 10 should return 5
        #   which is 5 - 10 + 10
        # and requesting 11 should return 6
        #   which is 5 - 10 + 11
        if self._taint:
            return self._taint[i]
        else:
            # self._t gets created only for empty strings.
            # use the exception to determine which ones need it.
            return self._t

    # returns the index of the character this substring maps to
    # e.g. "start" is the original string, "art" is the current string, then
    # "art".get_first_mapped_char() returns 2
    def get_first_mapped_char(self):
        """
        >>> my_str = tstr('abc')
        >>> my_str.get_first_mapped_char()
        0
        >>> my_str = tstr('abcdefghijkl', taint=list(range(4,16)))
        >>> my_str.get_first_mapped_char()
        4
        """
        for i in self._taint:
            if i >= 0:
                return i
        return -1

    # tpos is the index in the input string that we are
    # looking to see if contained in this string.
    def is_tpos_contained(self, tpos):
        """
        >>> my_str = tstr('abcdefghijkl', taint=list(range(4,16)))
        >>> my_str.is_tpos_contained(2)
        False
        >>> my_str.is_tpos_contained(4)
        True
        """
        return tpos in self._taint

    # idx is the string index of current string.
    def is_idx_tainted(self, idx):
        """
        >>> my_str = tstr('abcdefghijkl', taint=sum([list(range(4,10)), ([-1] * 6)],[]))
        >>> my_str.is_idx_tainted(2)
        True
        >>> my_str.is_idx_tainted(11)
        False
        """
        return self._taint[idx] != -1


    def __getitem__(self, key):          # splicing ( [ ] )
        """
        >>> my_str = tstr('abcdefghijkl', taint=list(range(4,16)))
        >>> my_str[0].x()
        4
        >>> my_str[-1].x()
        15
        >>> my_str[-2].x()
        14
        >>> s = my_str[0:4]
        >>> s.x(0)
        4
        >>> s.x(3)
        7
        """
        res = super().__getitem__(key)
        if type(key) == slice:
            if res:
                return tstr(res, self._taint[key], self)
            else:
                t = tstr(res, self._taint[key], self)
                key_start = 0 if key.start is None else key.start
                key_stop = len(res) if key.stop is None else key.stop
                if not len(t):
                    # is range start in str?
                    if key_start < len(self):
                        #is range end in str?
                        if key_stop < len(self):
                            t._t = self._taint[key_stop]
                        else:
                            t._t = len(self)
                    else:
                        t._t = len(self)
                return t

        elif type(key) == int:
            if key < 0:
                key = len(self) + key
            return tstr(res, [self._taint[key]], self)
        else:
            assert False

    def rsplit(self, sep = None, maxsplit = -1):
        """
        >>> my_str = tstr('ab cdef ghij kl', taint=list(range(0,15)))
        >>> ab, cdef, ghij, kl = my_str.rsplit(sep=' ')
        >>> ab.x()
        0
        >>> cdef.x()
        3
        >>> kl.x()
        13
        >>> my_str = tstr('ab   cdef ghij    kl', taint=list(range(0,20)))
        >>> ab, cdef, ghij, kl = my_str.rsplit()
        >>> ab.x()
        0
        >>> cdef.x()
        5
        >>> kl.x()
        18
        """
        splitted = super().rsplit(sep, maxsplit)
        if not sep: return self._split_space(splitted)

        result_list = []
        last_idx = 0
        first_idx = 0
        sep_len = len(sep)

        for s in splitted:
            last_idx = first_idx + len(s)
            item = self[first_idx:last_idx]
            result_list.append(item)
            # reset the first_idx
            first_idx = last_idx + sep_len
        return result_list

    def split(self, sep = None, maxsplit = -1):
        """
        >>> my_str = tstr('ab cdef ghij kl', taint=list(range(0,15)))
        >>> ab, cdef, ghij, kl = my_str.split(sep=' ')
        >>> ab.x()
        0
        >>> cdef.x()
        3
        >>> kl.x()
        13
        >>> my_str = tstr('ab   cdef ghij    kl', taint=list(range(0,20)))
        >>> ab, cdef, ghij, kl = my_str.split()
        >>> ab.x()
        0
        >>> cdef.x()
        5
        >>> kl.x()
        18
        """
        splitted = super().split(sep, maxsplit)
        if not sep: return self._split_space(splitted)

        result_list = []
        last_idx = 0
        first_idx = 0
        sep_len = len(sep)

        for s in splitted:
            last_idx = first_idx + len(s)
            item = self[first_idx:last_idx]
            result_list.append(item)
            # reset the first_idx
            first_idx = last_idx + sep_len
        global Comparisons
        Comparisons.append(Instr(Op.SPLIT_STR, self, sep))
        return result_list

    def _split_space(self, splitted):
        result_list = []
        last_idx = 0
        first_idx = 0
        sep_len = 0
        for s in splitted:
            last_idx = first_idx + len(s)
            item = self[first_idx:last_idx]
            result_list.append(item)
            v = str(self[last_idx:])
            sep_len = len(v) - len(v.lstrip(' '))
            # reset the first_idx
            first_idx = last_idx + sep_len
        return result_list

    def __add__(self, other):  #concatenation (+)
        """
        >>> my_str1 = tstr("abc")
        >>> my_str2 = tstr("def", taint=[4,5,6])
        >>> my_str3 = "ghi"
        >>> v = my_str1 + my_str2
        >>> v.x()
        0
        >>> v.x(2)
        2
        >>> v.x(3)
        4
        >>> w = my_str1 + my_str3
        >>> v.x()
        0
        """
        if type(other) is tstr:
            return tstr(str.__add__(self, other), (self._taint + other._taint), self)
        else:
            return tstr(str.__add__(self, other), (self._taint + [-1 for i in other]), self)

    def __radd__(self, other):  #concatenation (+) -- other is not tstr
        """
        >>> my_str1 = "abc"
        >>> my_str2 = tstr("def")
        >>> v = my_str1 + my_str2
        >>> v._x()
        -1
        >>> v._x(3)
        0
        """
        if type(other) is tstr:
            return tstr(str.__add__(other, self), (other._taint + self._taint), self)
        else:
            return tstr(str.__add__(other, self), ([-1 for i in other] + self._taint), self)

    def format(self, *args, **kwargs): #formatting (%) self is format string
        assert False
        return super().format(*args, **kwargs)

    def format_map(self, mapping): #formatting (%) self is format string
        assert False
        return super().format_map(mapping)


    def __mod__(self, other): #formatting (%) self is format string
        assert False
        return super().__mod__(other)

    def __rmod__(self, other): #formatting (%) other is format string
        return super().__rmod__(other)

    def strip(self, cl=None):
        """
        >>> my_str1 = tstr("  abc  ")
        >>> my_str1[2]
        'a'
        >>> v = my_str1.strip()
        >>> v.x()
        2
        >>> len(v)
        3
        >>> v[2]
        'c'
        >>> v[2].x()
        4
        """
        return self.lstrip(cl).rstrip(cl)

    def lstrip(self, cl=None):
        """
        >>> my_str1 = tstr("  abc  ")
        >>> my_str1[2]
        'a'
        >>> v = my_str1.lstrip()
        >>> v.x()
        2
        >>> v[2]
        'c'
        >>> v[2].x()
        4
        """
        res = super().lstrip(cl)
        i = self.find(res)
        return self[i:]

    def rstrip(self, cl=None):
        """
        >>> my_str1 = tstr("  abc  ")
        >>> my_str1[2]
        'a'
        >>> v = my_str1.rstrip()
        >>> v.x()
        0
        >>> v[2]
        'a'
        >>> v[2].x()
        2
        """
        res = super().rstrip(cl)
        return self[0:len(res)]

    def swapcase(self):
        """
        >>> my_str1 = tstr("abc")
        >>> v = my_str1.swapcase()
        >>> v[0].x()
        0
        >>> v[2].x()
        2
        """
        res = super().swapcase()
        return tstr(res, self._taint, self)

    def upper(self):
        """
        >>> my_str1 = tstr("abc")
        >>> v = my_str1.upper()
        >>> v[0].x()
        0
        >>> v[2].x()
        2
        """
        res = super().upper()
        return tstr(res, self._taint, self)

    def lower(self):
        """
        >>> my_str1 = tstr("abc")
        >>> v = my_str1.lower()
        >>> v[0].x()
        0
        >>> v[2].x()
        2
        """
        res = super().lower()
        return tstr(res, self._taint, self)

    def capitalize(self):
        """
        >>> my_str1 = tstr("abc")
        >>> v = my_str1.capitalize()
        >>> v[0].x()
        0
        >>> v[2].x()
        2
        """
        res = super().capitalize()
        return tstr(res, self._taint, self)

    def title(self):
        """
        >>> my_str1 = tstr("abc")
        >>> v = my_str1.title()
        >>> v[0].x()
        0
        >>> v[2].x()
        2
        """
        res = super().title()
        return tstr(res, self._taint, self)

    def __iter__(self):
        return tstr_iterator(self)

    def expandtabs(self, n=8):
        """
        >>> my_str = tstr("ab\\tcd")
        >>> len(my_str)
        5
        >>> my_str.split("\\t")
        ['ab', 'cd']
        >>> v = my_str.expandtabs(4)
        >>> v._taint
        [0, 1, 1, 1, 3, 4]
        """
        parts = self.split('\t')
        res = super().expandtabs(n)
        all_parts = []
        for i,p in enumerate(parts):
            all_parts.extend(p._taint)
            if i < len(parts)-1:
                l = len(all_parts) % n
                all_parts.extend([p._taint[-1]]*l)
        return tstr(res, all_parts, self)

    def partition(self, sep):
        partA, sep, partB = super().partition(sep)
        return (tstr(partA, self._taint[0:len(partA)], self), tstr(sep, self._taint[len(partA): len(partA) + len(sep)], self), tstr(partB, self._taint[len(partA) + len(sep):], self))

    def rpartition(self, sep):
        partA, sep, partB = super().rpartition(sep)
        return (tstr(partA, self._taint[0:len(partA)], self), tstr(sep, self._taint[len(partA): len(partA) + len(sep)], self), tstr(partB, self._taint[len(partA) + len(sep):], self))

    def ljust(self, width, fillchar=' '):
        res = super().ljust(width, fillchar)
        initial = len(res) - len(self)
        if type(fillchar) is tstr:
            t = fillchar.x()
        else:
            t = -1
        return tstr(res, [t] * initial + self._taint, self)

    def rjust(self, width, fillchar=' '):
        res = super().rjust(width, fillchar)
        final = len(res) - len(self)
        if type(fillchar) is tstr:
            t = fillchar.x()
        else:
            t = -1
        return tstr(res, self._taint + [t] * final, self)

    def join(self, iterable):
        mystr = ''
        mytaint = []
        sep_taint = self._taint 
        lst = list(iterable)
        for i,s in enumerate(lst):
            staint = s._taint if type(i) is tstr else [-1] * len(s)
            mytaint.extend(staint)
            if i <= len(lst):
                mytaint.extend(sep_taint)
        res = super().join(iterable)
        return tstr(res, mytaint, self)


    def __format__(self, formatspec):
        res = super().__format__(formatspec)
        assert False
        return res

    def __eq__(self, other):
        global Comparisons
        Comparisons.append(Instr(Op.EQ, self, other))
        return super().__eq__(other)

    def __ne__(self, other):
        global Comparisons
        Comparisons.append(Instr(Op.NE, self, other))
        return super().__ne__(other)

    def __contains__(self, other):
        global Comparisons
        Comparisons.append(Instr(Op.IN, self, other))
        return super().__contains__(other)

    def replace(self, a, b, n=None):
        """
        >>> my_str = tstr("aa cde aa")
        >>> res = my_str.replace('aa', 'bb')
        >>> res
        'bb cde bb'
        >>> res._taint
        [-1, -1, 2, 3, 4, 5, 6, -1, -1]
        """
        old_taint = self._taint
        b_taint = b._taint if type(b) is tstr else [-1] * len(b)
        mystr = str(self)
        i = 0
        while True:
            if n and i >= n: break
            idx = mystr.find(a)
            if idx == -1: break
            last = idx + len(a)
            mystr = mystr.replace(a, b, 1)
            partA, partB = old_taint[0:idx], old_taint[last:]
            old_taint = partA + b_taint + partB
            i += 1
        return tstr(mystr, old_taint, self)

    def count(self, sub, start=0, end=None):
        return super().count(start, end)

    def startswith(self, prefix, start=0, end=None):
        return super().startswith(prefix ,start, end)

    def endswith(self, suffix, start=0, end=None):
        return super().endswith(suffix ,start, end)

    # returns int
    def find(self, sub, start=None, end=None):
        global Comparisons
        Comparisons.append(Instr(Op.FIND_STR, self, sub))
        return super().find(sub, start, end)

    # returns int
    def index(self, sub, start=None, end=None):
        return super().index(sub, start, end)

    # returns int
    def rfind(self, sub, start=None, end=None):
        return super().rfind(sub, start, end)

    # returns int
    def rindex(self, sub, start=None, end=None):
        return super().rindex(sub, start, end)

    def isalnum(self): return super().isalnum()
    def isalpha(self): return super().isalpha()
    def isdigit(self): return super().isdigit()
    def islower(self): return super().islower()
    def isupper(self): return super().isupper()
    def isspace(self): return super().isspace()
    def istitle(self): return super().istitle()
    def isdecimal(self): return super().isdecimal()
    def isidentifier(self): return super().isidentifier()
    def isnumeric(self): return super().isnumeric()
    def isprintable(self): return super().isprintable()


# import pudb; brk = pudb.set_trace
def make_str_wrapper(fun):
    def proxy(*args, **kwargs):
        res = fun(*args, **kwargs)
        if res.__class__ == str:
            # brk()
            if fun.__name__ == '__mul__': #repeating (*)
                return tstr(res, idx=0)
            elif fun.__name__ == '__rmul__': #repeating (*)
                return tstr(res, idx=0)
            elif fun.__name__ == 'splitlines':
                return tstr(res, idx=0)
            elif fun.__name__ == 'center':
                return tstr(res, idx=0)
            elif fun.__name__ == 'zfill':
                return tstr(res, idx=0)
            elif fun.__name__ == 'decode':
                return tstr(res, idx=0)
            elif fun.__name__ == 'encode':
                return tstr(res, idx=0)
            else:
                raise Exception('%s Not implemented in TSTR' % fun.__name__)
        return res
    return proxy

for name, fn in inspect.getmembers(str, callable):
    if name not in ['__class__', '__new__', '__str__', '__init__', '__repr__',
            '__getattribute__', '__getitem__', '__rmod__', '__mod__', '__add__',
            '__radd__', 'strip', 'lstrip', 'rstrip', '__iter__', 'expandtabs',
            '__format__', 'split', 'rsplit', 'format', 'join',
            '__eq__', '__ne__', '__contains__', 'count',
            'startswith', 'endswith', 'find', 'index', 'rfind' 'rindex',
            'capitalize', 'replace', 'title', 'lower', 'upper', 'swapcase',
            'partition', 'rpartition', 'ljust', 'rjust',
            'isalnum', 'isalpha', 'isdigit', 'islower', 'isupper', 'isspace',
            'istitle', 'isdecimal', 'isidentifier', 'isnumeric', 'isprintable'
            ]:
        setattr(tstr, name, make_str_wrapper(fn))

def get_t(v):
    if type(v) is tstr: return v
    if hasattr(v, '__dict__') and '_tstr' in v.__dict__: return get_t(v._tstr)
    return None
