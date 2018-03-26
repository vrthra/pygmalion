from taintedstr import Op
import itertools as it
import pygmalion.miner as miner
import pygmalion.grammar as g
import pygmalion.config as config
import pygmalion.util as u
import sys
import os
import pickle
from pygmalion.bc import bc
import pudb; brk = pudb.set_trace

class Not:
    def __init__(self, v):
        self.v = v
    def __str__(self): return "[^%s]" % str(self.v.val())
    def __repr__(self): return "!%s" % str(self.v)
    def __bool__(self): return bool(self.v)

class Box:
    def __init__(self, v):
        self.v = v
    def val(self): return u.to_str(self.v)
    def __str__(self): return "[%s]" % self.val()
    def __repr__(self): return "<%s>" % ''.join(self.v)
    def __bool__(self): return len(''.join(self.v)) > 0

class Choice:
    def __init__(self, a, b):
        self.a, self.b = a, b
    def __repr__(self): return 'choice: %s' % str(self)
    def __str__(self):
        if self.a and not self.b:
            return str(self.a)
        elif self.a and not self.b:
            return str(self.b)
        else:
            return '(%s&%s)' % (self.a, self.b)
            #return '%s' % self.a
    def __eq__(self, o):
        return type(o) == Choice and str(self) == str(o)

def nt_key_to_s(i):
    v = i.k
    return "[%s:%s]" % (v.func, v.var)

def get_regex(cmps):
    # the input structure is a dict where keys are the instruction
    # numbers and each value is a list of secondary instructions in key:o.
    # or summaries in eq, ne, in, ni sne, fne, sni, sin etc.
    # First priority to all equals that succeeded
    # This is because we should be able to get a grammar that
    # will include this element.
    success_eq = set()
    failure_eq = set()
    assert not config.Python_Specific # we dont implement in, not in, neq etc yet.
    for i in cmps:
        kind, v = cmps[i]['charclass']
        if kind:
            success_eq.update(v)
        else:
            failure_eq.update(v)
    v = Choice(Box(success_eq), Not(Box(failure_eq)))
    return v

def normalize_char_cmp(elt, rule):
    """
    Convert EQ and IN both to similar arrays. EQ is a one element
    array while IN is a multi element array. The idea is to achieve
    a in [a] for _eq_ and a in [abcd] for _in_
    """
    regex = []
    for pos in elt._taint:
        if not pos in rule.comparisons: continue
        eltregex = get_regex(rule.comparisons[pos])
        regex.append(eltregex)
    return miner.RWrap(rule.k, regex, rule._taint, rule.comparisons)

def to_comparisons(rule):
    """
    The idea here is to shift away from individual results
    to the comparisons made.
    """
    rvalues = []
    for elt in rule.rvalues():
        if type(elt) is miner.NTKey:
            rvalues.append(elt)
        else:
            new_elt = normalize_char_cmp(elt, rule)
            rvalues.append(new_elt)
    return rvalues

def unique(rules):
    my_rules_set = {}
    for rule in rules:
        if str(rule) not in my_rules_set:
            my_rules_set[str(rule)] = rule
    return list(my_rules_set.values())

def rule_match_simple(mr, r):
    """
    Two rules match if they have same length, and each
    *comparison* in one correspond to another.
    Note that we can have a complex regex kind of rule
    match too -- not implemented here.
    """
    if len(mr) != len(r): return False
    for i, me in enumerate(mr):
        e = r[i]
        if all(i == miner.NTKey for i in [type(me), type(e)]):
            if me != e: return False
        if all(i == list for i in [type(me), type(e)]):
            if me != e: return False
        else:
            return False
    return True

def merge_rules(rules):
    """
    The idea here is that given a list of rules,
    start by construcing a new list out of the first rule.
    Then for each rule in the list, check if the new list
    contains* a corresponding rule. If not, add the rule
    to the new list. If yes, either merge the found rule
    and re-add or ignore the new rule.
    """
    my_rules = [rules[0]]
    for rule in rules[1:]:
        # does my_rule contain rule?
        append = True
        for mrule in my_rules:
            if rule_match_simple(mrule, rule):
                append = False
        if append:
            my_rules.append(rule)

    assert len(rules) == len(my_rules)
    return my_rules


def to_char_classes(rules):
    rules = unique(rules)
    new_rules = []
    for rule in rules:
        if config.Use_Character_Classes:
            r = to_comparisons(rule)
        else:
            r = rule
        new_rules.append(r)
    new_rules = merge_rules(new_rules)
    return new_rules

def max_compress_grammar(grammar):
    def to_k(k): return "[%s:%s]" % (k.k.func, k.k.var)
    def to_str(l):
        if type(l) is miner.NTKey: return to_k(l)
        else: return str(l)
    new_grammar = {}
    for k in grammar.keys():
        rules = grammar.get(k)
        key = k
        if key not in new_grammar: new_grammar[key] = []
        new_rules = []
        for rule in rules:
            new_rule = []
            last_en = None
            for elt in rule:
                if type(elt) is miner.NTKey:
                    en = elt
                else:
                    lasti = None
                    lst = []
                    for i in elt.rvalues:
                        if not lasti:
                            lasti = i
                            lst.append(i)
                            continue
                        if str(i) == str(lasti):
                            if lst[-1] != '+':
                                lst.append('+')
                            else:
                                pass
                        else:
                            lst.append(i)
                            lasti = i
                    en = miner.RWrap(elt.k, lst, elt._taint, elt.comparisons)
                if not last_en:
                    last_en = to_str(en)
                    new_rule.append(en)
                    continue
                if last_en == to_str(en):
                    if new_rule[-1]!= '+':
                        new_rule.append('+')
                    else:
                        pass
                else:
                    new_rule.append(en)
                    last_en = to_str(en)
            new_rules.append(new_rule)
        new_grammar[key].extend(new_rules)
    new_g = {}

    # now compress the rules for each keys
    for k in new_grammar:
        new_rules = {}
        for rules in new_grammar[k]:
            v = {str(r):r for r in rules}
            key = ''.join(list(v.keys()))
            new_rules[key] = list(v.values())
        new_grammar[k] = list(new_rules.values())
    return new_grammar

def get_key_set(short_keys):
    all_keys = {}
    for k in short_keys.keys():
        sk = short_keys[k]
        if sk not in all_keys: all_keys[sk] = set()
        all_keys[sk].add(k)
    return all_keys

def to_k(k): return "[%s:%s]" % (k.k.func, k.k.var)

def is_rule_in_ruleset(r, ruleset):
    def val(x): return str([str(i) for i in x])
    return any(rule_match_simple(s,r) for s in ruleset)

def subrule_of(k, key_set, grammar):
    small_rules = grammar[k]
    for key in key_set:
        if k == key: continue
        large_rules = grammar[key]
        if all(is_rule_in_ruleset(r,large_rules) for r in small_rules):
            return key
    return None

def remove_subset_keys(grammar):
    # The idea is to remove those keys that are completely subsets of another
    # key with the same stem
    lst = [(k, grammar[k]) for k in grammar.keys()]
    short_keys = {k:to_k(k) for k in grammar.keys()}
    all_keys = get_key_set(short_keys)
    to_remove = set()
    for short_key in all_keys:
        #if '_from_json_dict:c' in str(short_key): brk()
        key_set = all_keys[short_key]
        for k in key_set:
            large_k = subrule_of(k, key_set, grammar)
            if large_k and large_k not in to_remove:
                to_remove.add((k, large_k))
    new_grammar = {}
    rks = {k for k,lk in to_remove}
    for k in grammar.keys():
        if k in rks: continue
        new_grammar[k] = grammar[k]

    for k in new_grammar:
        rules = grammar[k]
        for r in rules:
            if k in r:
                replace(k, lk)
    return new_grammar

def remove_multiple_repeats_from_elt(elt):
    if type(elt) == miner.NTKey: return elt
    if len(elt.rvalues) == 1: return elt
    rv = remove_multiple_repeats_from_lst(elt.rvalues)
    elt.rvalues = rv
    return elt

def remove_multiple_repeats_from_lst(lst):
    # make them triplets
    tpls = it.zip_longest(lst, lst[1:], lst[2:])
    #return [a for (a,b,c) in tpls if not (a == b and b == c)]
    lst = []
    for a,b,c in tpls:
        if (a == b and b == c): continue
        lst.append(a)
    return lst


def remove_multi_repeats_from_rule(rule):
    new_elts = []
    for elt in rule:
        e = remove_multiple_repeats_from_elt(elt)
        new_elts.append(e)
    elts = remove_multiple_repeats_from_lst(new_elts)
    return elts


def remove_multi_repeats(g):
    for k in g:
        rs = g[k]
        new_rs = []
        for r in rs:
            new_r = remove_multi_repeats_from_rule(r)
            new_rs.append(r)
        g[k] = new_rs
    return g

def refine_grammar(grammar):
    g = {k:unique(to_char_classes(grammar._dict[k])) for k in grammar._dict}
    # g = remove_subset_keys(g)
    if config.Sort_Grammar:
        g = {k:sorted(g[k], key=lambda x: str(x))
                for k in sorted(g.keys(), key=lambda x: str(x))}

    if 'single_repeat' in config.Refine_Tactics:
        g = remove_multi_repeats(g)

    if config.Max_Compress_Grammar: g =  max_compress_grammar(g)
    return g

