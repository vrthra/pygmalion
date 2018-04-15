import pygmalion.grammar as g
import pygmalion.config as config
import pygmalion.refiner as refiner
import pygmalion.miner as miner
import pygmalion.util as u
import pudb
import sys
from taintedstr import Op
brk = pudb.set_trace


def get_regex_map(parse_tree, xcmps, inp):
    comparison_map = {}
    for k in parse_tree.keys():
        rule = parse_tree[k]
        assert len(rule) == 1
        r = list(rule)[0]
        r.comparisons = {i:xcmps[i] for i in r.taint if i < len(xcmps)}
        r._input = inp
        if k.k == g.V.start():
            newk = k
        else:
            hkey = []
            for pos in r._taint:
                val = str(get_regex(r.comparisons[pos]))
                hkey.append(val)
            newk = miner.NTKey(k.k.newV(u.h1(':'.join(hkey))))
        comparison_map[k] = newk
    return comparison_map

def translate_keys(parse_tree, comparison_map):
    nlg = {}
    for k in parse_tree.keys():
        hk = comparison_map[k]
        rules = parse_tree[k]
        newrules = set()
        for rule in rules:
            new_rule = []
            for elt in rule:
                newelt = None
                if type(elt) == miner.NTKey:
                    newk = comparison_map[elt]
                    newelt = newk
                else:
                    newelt = elt
                new_rule.append(newelt)
            newr = rule.to_rwrap(new_rule)
            newrules.add(newr)
        if hk in nlg:
            nlg[hk].update(newrules)
        else:
            nlg[hk] = newrules
    return nlg


def merge_grammars(g1, parse_tree, xcmps, inp):
    comparison_map = get_regex_map(parse_tree, xcmps, inp)
    nlg = g.Grammar(translate_keys(parse_tree, comparison_map))
    my_g = {}
    for key in g1.keys() + nlg.keys():
        v = g1[key] | nlg[key]
        my_g[key] = v
    return g.Grammar(my_g)
    # return g.Grammar({key: g1[key] | parse_tree[key] for key in g1.keys() + parse_tree.keys()})

def process_one_op(v, pos):
    if not v: assert False
    opA = set(i.opA for i in v)
    assert len(opA) == 1
    opA = opA.pop()

    if not config.Python_Specific:
        # The idea is that if opA is in atleast one of v, then
        # it is an equality character class. Else it is an not in char class
        assert all(Op(i.op) == Op.EQ for i in v)
        c_eq = any(i.opB for i in v if i.opA == i.opB)
        chars = [i.opB for i in v]

        return {'pos':pos, 'opA':opA, 'o':v, 'charclass':(c_eq, chars)}
    else:
        assert False # -- this is out of date. Needs to be fixed

def process_one_instruction(pos, v):
    # split into separate operations
    ins_set = set(c for i,c in v)
    ops = {}
    for op_c in ins_set:
        op = [i for i,c in v if c == op_c]
        ops[op_c] = process_one_op(op, op_c)
    return ops


def separate_comparisons_per_char(xins):
    cmps, icmps = xins
    outputs = {}
    for i,o in enumerate(cmps):
        op = o.op_A.x()
        if op not in outputs: outputs[op] = []
        outputs[op].append((o, icmps[i]))
    return outputs

def process_comparisons_per_char(ins):
    lst = sorted(ins.keys())
    vals = []
    for pos in lst:
        # v is a list of trace ops for position pos
        v = ins[pos]
        vals.append(process_one_instruction(pos, v))
    return vals
# --
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
    v = refiner.Choice(refiner.Box(success_eq), refiner.Not(refiner.Box(failure_eq)))
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
    return regex

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
    return rule.to_rwrap(rvalues)

def unique_rules(rules):
    my_rules_set = {}
    for rule in rules:
        if str(rule) not in my_rules_set:
            my_rules_set[str(rule)] = rule
    return list(my_rules_set.values())

def rule_match_simple(rwmr, rwr):
    """
    Two rules match if they have same length, and each
    *comparison* in one correspond to another.
    Note that we can have a complex regex kind of rule
    match too -- not implemented here.
    """
    mr = rwmr.rvalues()
    r = rwr.rvalues()

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

    assert len(rules) >= len(my_rules)
    return my_rules


def to_char_classes(rules):
    rules = unique_rules(rules)
    new_rules = []
    for rule in rules:
        if config.Use_Character_Classes:
            r = to_comparisons(rule)
        else:
            r = rule
        new_rules.append(r)
    new_rules = merge_rules(new_rules)
    return new_rules

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
    if len(elt) == 1: return elt
    rv = remove_multiple_repeats_from_lst(elt.rvalues())
    elt._rvalues = rv
    return elt

def remove_multiple_repeats_from_lst(lst):
    if len(lst) < 3:
        return lst
    # make them triplets
    tpls = it.zip_longest(lst, lst[1:], lst[2:])
    lst = []
    for a,b,c in tpls:
        if (a == b and b == c): continue
        lst.append(a)
    return lst
    # return [a for (a,b,c) in tpls if not (a == b and b == c)]


def remove_multi_repeats_from_rule(rule):
    elts = []
    for c in rule.rvalues():
        if type(c) is list:
            c_ = remove_multiple_repeats_from_lst(c)
        else:
            c_ = c
        elts.append(c_)
    return rule.to_rwrap(elts)


def remove_multi_repeats(g):
    for k in g:
        rs = g[k]
        new_rs = []
        for r in rs:
            new_r = remove_multi_repeats_from_rule(r)
            new_rs.append(new_r)
        new_rs = remove_multiple_repeats_from_lst(new_rs)
        g[k] = new_rs
    return g

def replace_key_in_rule(k, vr, my_r):
    replaced = False
    ret_r = []
    if type(vr) is miner.NTKey:
        v = vr
    elif type(vr) is miner.RWrap:
        v = vr.rvalues()[0]
    else:
        assert False
    for elt in my_r.rvalues():
        if type(elt) == type(k) and elt == k:
            replaced = True
            # expand v because it is a complete sequence
            newelt = v
        else:
            newelt = elt
        ret_r.append(newelt)
    return (replaced, my_r.to_rwrap(ret_r))

def remove_single_alternatives(g):
    # given key := value with no alternatives, replace
    # any instance of tht key with the value.
    while True:
        replaced = False
        glst = [(k,g[k]) for k in g]
        single_keys = {}
        for k,v in glst:
            if len(v) == 1:
                # this is a list of rules
                rule = v[0]
                rv = rule.rvalues()
                if len(rv) == 1:
                    if  type(rv[0]) is miner.NTKey:
                        single_keys[k] = rv[0]
        newg = {}
        for key in g:
            rset = g[key]
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
        newg = grammar_gc(newg)
        if not replaced: return newg
        assert l > len(newg)
        g = newg
    assert False

def grammar_gc(grammar):
    # Removes any unused keys if one starts from START and adds
    # all referencing keys in rules recursively
    start = miner.NTKey(g.V.start())
    keys = [start]
    seen = set(keys)
    new_g = {}
    while keys:
        k, *keys = keys
        new_g[k] = grammar[k]
        rules = grammar[k]
        for rule in rules:
            for e in rule.rvalues():
                if type(e) is miner.NTKey and e not in seen:
                    seen.add(e)
                    keys.append(e)
    return new_g

def compress_rules(rules):
    # Removes duplicate rules (where all (str(rule) are exactly equal)
    seen = {}
    for r in rules:
        if r not in seen:
            seen[str(r)] = r
    return list(seen.values())

def compress_keys(grammar):
    # Removes duplicate keys (where all (str(rules) are exactly equal)
    while True:
        replaced = False
        glst = {k:u.djs_to_string(grammar[k]) for k in grammar}
        replacements = []
        for k1 in glst:
            v1 = glst[k1]
            for k2 in glst:
                if k1 == k2: continue
                v2 = glst[k2]
                if v1 == v2:
                    replacements.append((k2, k1))
        newg = None
        newg = {}
        for k in grammar:
            rules = grammar[k]
            new_rules = []
            for rule in rules:
                new_rule = rule
                for k2, k1 in replacements:
                    rep, new_rule = replace_key_in_rule(k2, k1, rule)
                    if rep:
                        # print("In ", k, ":", k2, "=>", k1)
                        replaced = True
                new_rules.append(new_rule)
            newg[k] = new_rules
        if not replaced: return newg
        l = len(grammar)
        newg = grammar_gc(newg)
        assert l > len(newg)
        grammar = newg
    assert False

# --

# Get a grammar for multiple inputs
def infer_grammar(parse_trees):
    merged_grammar = g.Grammar()
    for j, (i, xins, parse_tree) in enumerate(parse_trees):
        print("infer:", j, i, file=sys.stderr, flush=True)
        # this is for a single input
        xcmps = process_comparisons_per_char(separate_comparisons_per_char(xins))
        merged_grammar = merge_grammars(merged_grammar, parse_tree, xcmps, i)


    if config.With_Char_Class:
        grammar = merged_grammar
        newg = {}
        for k in grammar.keys():
            v = grammar.get(k)
            cv = to_char_classes(v)
            newg[k] = set(unique_rules(cv))
    else:
        newg = merged_grammar
    return g.Grammar(newg)
