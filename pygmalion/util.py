import json
import string
import hashlib
import itertools as it
from pygmalion.bc import bc
import pudb
brk = pudb.set_trace

green = bc(bc.green)

def lossy_obj_rep(val):
    if isinstance(val, list):
        return [lossy_obj_rep(i) for i in val]
    elif isinstance(val, set):
        return {lossy_obj_rep(i) for i in val}
    elif isinstance(val, dict):
        return {str(i):lossy_obj_rep(val[i]) for i in val}
    elif hasattr(val, '__dict__'):
        return ('#' + val.__class__.__name__, lossy_obj_rep(val.__dict__))
    else:
        try:
            s = json.dumps(val)
            return val
        except:
            try:
                return '<not serializable #%s %s>' % (val.__class__.__name__, hash(val))
            except:
                return '<not serializable #%s %s>' % (val.__class__.__name__, str(val))
def my_str(v):
    if type(v) is list:
        return ''.join([str(i) for i in v])
    else:
        return str(v)


def elts_to_str(lstrule):
    return ''.join(my_str(i) for i in lstrule.rvalues())

def djs_to_string(djs):
    vals = [elts_to_str(i).replace('\n', '\n|\t') for i in djs]
    return "\n\t| ".join(vals)

def fixline(key, rules):
    fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
    return fmt % (key, djs_to_string(rules))

def with_repeating_numbers(g):
    ng = []
    for k in g:
        rules = g[k]
        nrules = []
        for rule in rules:
            nrule = []
            for elt in rule.rvalues():
                if type(elt) is list:
                    nelt = [(c, len(list(cgen))) for c,cgen in it.groupby(elt)]
                    myelt = []
                    for e,count in nelt:
                        if count > 1:
                            myelt.append("%s{%d}" % (str(e), count))
                        else:
                            myelt.append("%s" % str(e))
                    nelt = ''.join(myelt)
                else:
                    nelt = str(elt)
                nrule.append(nelt)
            nrule = ''.join(nrule)
            nrules.append(nrule)
        nrules = '\n\t|  '.join(sorted(nrules))
        fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t|  %s"
        fmtd = fmt % (k, nrules)
        ng.append(fmtd)
    res = "\n".join(ng)
    return res

def choice_to_bnf(c):
    assert type(c) is tuple
    choice, count = c
    cv = choice.a if choice.a else choice.b
    strcv = compact(str(cv))
    if type(count) is set:
        fst = min(count)
        lst = max(count)
        return "%s{%d,%d}" % (strcv, fst, lst)
    else:
        if count == 1:
            return "%s" % strcv
        else:
            return "%s{%d}" % (strcv, count)

def elt_to_bnf(elt):
    if type(elt) is tuple:
        return choice_to_bnf(elt)
    else:
        return str(elt)

def get_choice(c):
    if c.a: return c.a
    else: return c.b

def escape(s):
    s = s.replace('[', '\\[')
    s = s.replace(']', '\\]')
    s = s.replace('(', '\\(')
    s = s.replace(')', '\\)')
    s = s.replace('+', '\\+')
    s = s.replace('*', '\\*')
    s = s.replace('?', '\\?')
    return s

def compact(s):
    s = s.replace('0123456789', '0-9')
    s = s.replace('abcdefghijklmnopqrstuvwxyz', 'a-z')
    s = s.replace('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'A-Z')
    return s

def item_to_bnf(elt):
    if hasattr(elt, 'a'):
        v = get_choice(elt)
        if 'Box' in str(type(v)) and len(v.v) == 1:
            return "%s" % escape(str(list(v.v)[0]))
        else:
            return compact(str(v))
    else:
        return elt_to_bnf(elt)

def rule_to_bnf(rule):
    nrule = [(c, len(list(cgen))) for c,cgen in it.groupby(rule, key=item_to_bnf)]
    res = []
    for elt, l in nrule:
        if l == 1:
            res.append(elt)
        else:
            res.append("%s{%d}" % (elt, l))
    return ''.join(res)
    #return ''.join(elt_to_bnf(elt) for elt in rule)

def alter_to_bnf(k, rules):
    fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n    | %s"
    alters = {rule_to_bnf(rule) for rule in rules}
    return fmt % (k, "\n    | ".join(sorted(list(alters))))

def g_to_bnf(g):
    return '\n'.join([alter_to_bnf(k,g[k]) for k in g])

def readable_grammar(g):
    return g_to_bnf(g)

def show_grammar(g):
    res = with_repeating_numbers(g)
    return res

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

Hash = {}

def h1(w):
    global Hash
    v = hashlib.sha256(w.encode('utf-8')).hexdigest()[0:8]
    if v in Hash:
        s = Hash[v]
        assert w == s
    else:
        Hash[v] = w
    return v
