from taintedstr import Op
import pygmalion.miner as miner
import pygmalion.grammar as g
import pygmalion.config as config
import sys
import os
import pickle
from pygmalion.bc import bc
import pudb; brk = pudb.set_trace

class Not:
    def __init__(self, v):
        self.v = v

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

def phase_1(elt, rule):
    regex = []
    for pos in elt._taint:
        # get the original
        cmps = rule.comparisons[pos]['o']
        # get last comparison made
        last = cmps[-1]
        op_A = str(last.op_A)
        op_B = str(last.op_A)
        op_Bs = [str(i) for i in last.op_B]
        if last.op == Op.EQ:
            if op_A == op_B: regex.append([op_B])
            else: regex.append(Not([op_B]))
        elif last.op == Op.NE:
            if op_A == op_B: regex.append(Not([op_B]))
            else: regex.append([op_B])
        elif last.op == Op.IN:
            if op_A in op_Bs: regex.append(op_Bs)
            else: regex.append(Not(op_Bs))
        elif last.op == Op.NOT_IN:
            if op_A in op_Bs: regex.append(Not(op_Bs))
            else: regex.append(op_Bs)

    return regex

def to_regex(rule):
    rvalues = []
    for elt in rule.rvalues():
        if type(elt) is miner.NTKey:
            rvalues.append(elt)
        else:
            new_elt = phase_1(elt, rule)
            rvalues.append(new_elt)
    return rvalues

def unique(rules):
    my_rules_set = {}
    for rule in rules:
        if str(rule) not in my_rules_set:
            my_rules_set[str(rule)] = rule
    return list(my_rules_set.values())

def rule_match(mr, r):
    return False

def merge_rules(rules):
    my_rules = []
    for rule in rules:
        if not my_rules:
            my_rules.append(rule)
            continue
        new_rules = []
        for mrule in my_rules:
            if rule_match(mrule, rule):
                mr = merge_rule(mrule, rule)
                new_rules.append(mr)
            else:
                new_rules.append(mrule)
                new_rules.append(rule)
        my_rules = new_rules
    assert len(rules) == len(my_rules)
    return my_rules


def compress_rules(rules):
    rules = unique(rules)
    new_rules = []
    for rule in rules:
        r = to_regex(rule)
        new_rules.append(r)
    new_rules = merge_rules(new_rules)
    return new_rules


def refine_grammar(grammar):
    return {k:compress_rules(grammar._dict[k]) for k in grammar._dict}

