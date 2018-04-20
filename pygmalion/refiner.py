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

def count_elements(grammar):
    ng = {}
    for k in grammar:
        rules = grammar[k]
        nrules = []
        for rule in rules:
            nrule = list()
            for elt in rule.rvalues():
                if type(elt) is list:
                    # a list of choices
                    nelt = [(c, len(list(cgen))) for c,cgen in it.groupby(elt)]
                else:
                    nelt = elt
                nrule.append(nelt)
            nrules.append(rule.to_rwrap(nrule))
        ng[k] = nrules
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
            newrules.append(rule.to_rwrap(newrule))
        ng[k] = newrules
    return ng

def are_choices_same(list_of_choices):
    my_choice = {str(choice) for choice, count in list_of_choices}
    my_counts = {count for choice, count in list_of_choices}
    if len(my_choice) > 1: return False
    return (list_of_choices[0][0], my_counts)

def are_elements_same(elts):
    # taking elements of each rules,
    # make sure we are talking about similar elements e.g ntkey = ntkey
    stype = {type(i) for i in elts}
    # else cant compress the rule
    if len(stype) != 1: return False

    # If they are all exactly the same, we have no issues
    sstr = set(str(i) for i in elts)
    if len(sstr) == 1: return elts[0]

    if  tuple in stype:
        res = are_choices_same(elts)
        if not res: return False
        return res
    else:
        # different NTKeys
        return False

def compress_grouped_rules(llen, rules):
    if len(rules) == 1:
        res = are_elements_same(rules[0])
        if not res: return rules
        return [[res]]
    new_rule = []
    for k in zip(*rules):
        res = are_elements_same(k)
        if not res: return rules
        new_rule.append(res)
    return [new_rule]

def plain_expand(elts):
    res = []
    for i in elts:
        if type(i) is g.NTKey:
            res.append(str(i))
        else:
            assert type(i) is tuple
            k, count = i
            res.append(str(k))
    return ''.join(res)

def compress_alternative_with_set_count(k, rules):
    # take the set of alternatives, group them by their length
    # then for each group, start with the first element, and check
    # if elements are the same. If they are a choice with different
    # count but same char set, it is considered the same. It returns
    # the set of counts instead of a single count. and returns the
    # combined rule.
    # If they are not the same, each rule is returned separately
    # (hence the extend)
    expanded_rules = [l.rvalues() for l in sorted(rules, key=plain_expand)]
    new_rules = []
    for c, cgen in it.groupby(expanded_rules, key=plain_expand):
        v = compress_grouped_rules(c, list(cgen))
        for r in v:
            new_rules.append(g.Rule(k, r))
    return new_rules

def compress_grammar_alternatives(grammar):
    ng = {}
    for k in grammar:
        rules = grammar[k]
        ng[k] = compress_alternative_with_set_count(k, rules)
    return ng


def remove_self_repetition(grammar):
    # If a rule is of the form
    # key ::=
    #       key
    #      | rule rest
    # skip key
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = []
        for rule in rules:
            if len(rule.rvalues()) == 1 and str(rule.rvalues()[0]) == str(k):
                continue
            newrules.append(rule)
        ng[k] = newrules
    return ng

def expand_every_thing(grammar):
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = []
        for rule in rules:
            newrule = []
            for elt in rule.rvalues():
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

def simplify_choices(grammar):
    # change all choices from either box or not box
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = set()
        for rule in rules:
            newrule = []
            for elt in rule.rvalues():
                if type(elt) is list:
                    clist = []
                    for c in elt:
                        if type(c) is g.Choice:
                            cx = c.a if c.a else c.b
                            clist.append(cx)
                        else:
                            clist.append(c)
                    newrule.append(clist)
                else:
                    newrule.append(elt)
            newrules.add(rule.to_rwrap(newrule))
        ng[k] = newrules
    return ng

def generalize_sets(grammar):
    # Replace a set by just its min and max values
    ng = {}
    for k in grammar:
        rules = grammar[k]
        newrules = []
        for rule in rules:
            newrule = []
            for elt in rule.rvalues():
                if type(elt) is g.NTKey:
                    newrule.append(elt)
                else:
                    choice, count = elt
                    if type(count) is set:
                        newrule.append((choice, set(range(min(count),max(count)))))
                    else:
                        newrule.append((choice, count))
            newrules.append(rule.to_rwrap(newrule))
        ng[k] = newrules
    return ng

def refine_grammar(grammar):
    assert type(grammar) is dict
    grammar = simplify_choices(grammar)

    assert type(grammar) is dict
    # given key := value with no alternatives, replace
    # any instance of tht key with the value.
    print('remove_single_alternatives', file=sys.stderr)
    grammar = remove_single_alternatives(grammar)

    grammar = g.grammar_complete_gc(grammar)

    grammar = count_elements(grammar)

    # make <key> [choice_char1, choice_char2] <key> [choice_char3]
    # into <key> choice_char1 choice_char2 <key> choice_char3
    grammar = flatten_choices(grammar)

    grammar = compress_grammar_alternatives(grammar)

    grammar = remove_self_repetition(grammar)

    grammar = generalize_sets(grammar)

    return grammar

