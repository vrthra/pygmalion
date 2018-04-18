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

def simplify_grammar(g):
    new_g = g
    new_g = count_elements(new_g)
    new_g = flatten_choices(new_g)
    new_g = compress_grammar(new_g)
    new_g = remove_redundant(new_g)
    new_g = expand_every_thing(new_g)
    return new_g

def expand_every_thing(grammar):
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = []
        for rule in rules:
            newrule = []
            for elt in rule:
                if type(elt) is tuple:
                    if type(elt[1]) is set:
                        newrule.append(elt)
                    else:
                        newrule.extend([elt[0]] * elt[1])
                else:
                    newrule.append(elt)
            newrules.append(newrule)
        ng[k] = newrules
    return ng


def remove_redundant(grammar):
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = []
        for rule in rules:
            newrule = []
            if len(rule) == 1 and str(rule[0]) == str(k):
                continue
            newrules.append(rule)
        ng[k] = newrules
    return ng

def flatten_choices(grammar):
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = []
        for rule in rules:
            newrule = []
            for elt in rule:
                if type(elt) == list:
                    newrule.extend(elt)
                else:
                    newrule.append(elt)
            newrules.append(newrule)
        ng[k] = newrules
    return ng


def are_elements_same(elts):
    # taking elements of each rules,
    # make sure we are talking about similar elements e.g ntkey = ntkey
    v = list({type(i) for i in elts})
    # else cant compress the rule
    if len(v) != 1: return False
    my_type = v[0]
    # make sure all nt keys are same
    stype = set(type(i) for i in elts)
    if len(stype) != 1: return False

    sstr = set(str(i) for i in elts)
    if len(sstr) == 1: return elts[0]
    if tuple in stype:
        res = are_choices_same(elts)
        if not res: return False
        return res
    else:
        # not choices
        return False

def are_choices_same(list_of_choices):
    my_choice = {str(choice) for choice, count in list_of_choices}
    my_counts = {count for choice, count in list_of_choices}
    if len(my_choice) > 1: return False
    return (list_of_choices[0][0], my_counts)



def compress_grouped_rules(rules):
    if len(rules) == 1: return rules
    new_rule = []
    for k in zip(*rules):
        res = are_elements_same(k)
        if not res: return rules
        new_rule.append(res)
    return [new_rule]

def compress_rules(rules):
    new_rules = []
    for c, cgen in it.groupby(rules, key=len):
        v = compress_grouped_rules(list(cgen))
        new_rules.extend(v)
    return new_rules

def compress_grammar(g):
    ng = {}
    for k in g:
        rules = g[k]
        ng[k] = compress_rules(rules)
    return ng

def count_elements(g):
    ng = {}
    for k in g:
        rules = g[k]
        nrules = []
        for rule in rules:
            nrule = []
            for elt in rule.rvalues():
                if type(elt) is list:
                    nelt = [(c, len(list(cgen))) for c,cgen in it.groupby(elt)]
                else:
                    nelt = elt
                nrule.append(nelt)
            nrules.append(nrule)
        ng[k] = nrules
    return ng

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
    res = simplify_grammar(g)
    return g_to_bnf(res)

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
