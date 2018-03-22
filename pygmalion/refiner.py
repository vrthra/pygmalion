from taintedstr import Op
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

class Box:
    def __init__(self, v):
        self.v = v
    def val(self): return u.to_str(self.v)
    def __str__(self): return "[%s]" % self.val()
    def __repr__(self): return "<%s>" % ''.join(self.v)

def nt_key_to_s(i):
    v = i.k
    return "[%s:%s]" % (v.func, v.var)

def char_class_process(lststr):
    i = 0
    last = None
    res = []
    plus = '+'
    while i < len(lststr):
        v = lststr[i]
        i = i+1
        if v == '+':
            res.append('['+ '+' + ']')
            continue
        if len(res) == 0:
            res.append(v)
            continue
        if res[-1] == plus:
            if v == res[-2]:
                pass
            else:
                res.append(v)
        else:
            if v == res[-1]:
                res.append(plus)
            else:
                res.append(v)
    return ''.join(res)

def to_str(i):
    if isinstance(i, str):
        return i
    elif isinstance(i, list):
        return ''.join(i)
    else:
        return type(i).__name__ + ':' + str(i)

def normalize_char_cmp(elt, rule):
    """
    Convert EQ and IN both to similar arrays. EQ is a one element
    array while IN is a multi element array. The idea is to achieve
    a in [a] for _eq_ and a in [abcd] for _in_
    """
    regex = []
    for pos in elt._taint:
        # get the original
        cmps = rule.comparisons[pos]
        # First priority to all equals that succeeded
        # This is because we should be able to get a grammar that
        # will include this element.
        slast = cmps['slast']
        if not slast:
            eq_cmp = set(cmps['eq'])
            ne_cmp = set(cmps['ne'])
            in_cmp = set(cmps['in'])
            ni_cmp = set(cmps['ni'])

            if eq_cmp:
                regex.append(Box(eq_cmp))
            elif in_cmp:
                regex.append(Box(in_cmp))
            elif ne_cmp:
                regex.append(Not(Box(ne_cmp)))
            elif ni_cmp :
                regex.append(Not(Box(ni_cmp)))
        else:
            eq_cmp =  [i for i in slast if Op(i.op) == Op.EQ]
            ne_cmp =  [i for i in slast if Op(i.op) == Op.NE]
            inv_cmp = [i for i in slast if Op(i.op) == Op.IN]
            nin_cmp = [i for i in slast if Op(i.op) == Op.NOT_IN]

            seq = [i.op_B for i in eq_cmp if i.opA == i.opB]
            feq = [i.op_B for i in eq_cmp if i.opA != i.opB]

            sne = [i.op_B for i in ne_cmp if i.opA != i.opB]
            fne = [i.op_B for i in ne_cmp if i.opA == i.opB]

            sin = [i.op_B for i in inv_cmp if i.opA in i.opB]
            fin = [i.op_B for i in inv_cmp if i.opA not in i.opB]

            sni = [i.op_B for i in nin_cmp if i.opA not in i.opB]
            fni = [i.op_B for i in nin_cmp if i.opA in i.opB]

            all_eq = seq + fne
            all_ne = sne + feq

            all_in = sin + fni
            all_ni = sni + fin

            # this was from the last *successful comparison*
            # so we can simply add everything together
            scheck = sorted(seq + feq)
            fcheck = sorted(sne + fne)
            if scheck:
                regex.append(Box(scheck))
            elif fcheck:
                regex.append(Not(Box(scheck)))
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


def compress_rules(rules):
    rules = unique(rules)
    new_rules = []
    for rule in rules:
        r = to_comparisons(rule)
        new_rules.append(r)
    new_rules = merge_rules(new_rules)
    return new_rules

def compress_grammar(grammar):
    # TODO: Before compressing, verify that the comparisons are indeed
    # same. If not, it may be better to keep them separate.
    def to_k(k): return "[%s:%s]" % (k.k.func, k.k.var)
    new_grammar = {}
    for k in grammar.keys():
        rules = grammar.get(k)
        key = to_k(k)
        if key not in new_grammar: new_grammar[key] = []
        new_rules = []
        for rule in rules:
            new_rule = []
            last_en = None
            for elt in rule:
                if type(elt) is miner.NTKey:
                    en = to_k(elt)
                else:
                    lasti = None
                    lst = []
                    for i in elt.rvalues:
                        if not lasti:
                            lasti = i
                            lst.append(str(i))
                            continue
                        if str(i) == str(lasti):
                            if lst[-1] != '+':
                                lst.append('+')
                            else:
                                pass
                        else:
                            lst.append(str(i))
                            last_i = i
                    en = ''.join(lst)
                if not last_en:
                    last_en = en
                    new_rule.append(en)
                    continue
                if last_en == en:
                    if new_rule[-1]!= '+':
                        new_rule.append('+')
                    else:
                        pass
                else:
                    new_rule.append(en)
                    last_en = en
            srule = ''.join(new_rule)
            new_rules.append(srule)
        new_grammar[key].extend(new_rules)
    new_g = {}
    for k in new_grammar:
        new_g[k] = set(str(i) for i in new_grammar[k])
    return new_g


def refine_grammar(grammar):
    g = {k:unique(compress_rules(grammar._dict[k])) for k in grammar._dict}
    if config.Compress_Grammar:
        return compress_grammar(g)
    else:
        return g

