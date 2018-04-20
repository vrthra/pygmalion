import itertools as it
import pygmalion.grammar as g
import pygmalion.config as config
import pygmalion.util as u
import sys
import pudb; brk = pudb.set_trace

def replace_key_in_rule(k, vrs, my_r):
    replaced = False
    ret_r = []
    assert type(vrs) is list
    for elt in my_r.rvalues():
        if type(elt) == type(k) and elt == k:
            replaced = True
            ret_r.extend(vrs)
        else:
            ret_r.append(elt)
    return (replaced, my_r.to_rwrap(ret_r))

def remove_single_alternatives(grammar):
    # given key := value with no alternatives, replace
    # any instance of tht key with the value.
    while True:
        replaced = False
        single_keys = {}
        for k,rs in grammar.items():
            if len(rs) == 1:
                # this is a list of rules
                rule = list(rs)[0]
                rv = rule.rvalues()
                # perhaps check if rv is a single element, and that element is a
                # string literal?
                single_keys[k] = rv
        newg = {}
        for key in grammar:
            rset = grammar[key]
            newrset = []
            for r in rset:
                my_r = r
                for k in single_keys:
                    replaced_by = single_keys[k]
                    if k == key: continue
                    rep, my_r = replace_key_in_rule(k, replaced_by, my_r)
                    if rep: replaced = True
                newrset.append(my_r)
            newg[key] = newrset
        l = len(newg.keys())
        newg = g.grammar_gc(newg)
        if not replaced: return newg
        assert l > len(newg)
        grammar = newg
    assert False

def refine_grammar(grammar):
    assert type(grammar) is dict
    if 'remove_single_alternatives' in config.Refine_Tactics:
        # given key := value with no alternatives, replace
        # any instance of tht key with the value.
        print('remove_single_alternatives', file=sys.stderr)
        grammar = remove_single_alternatives(grammar)

    assert type(grammar) is dict
    grammar = g.grammar_complete_gc(grammar)

    return grammar

