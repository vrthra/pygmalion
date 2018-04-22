import pygmalion.grammar as g
import pygmalion.config as config
import pygmalion.util as u
import pudb
import sys
from taintedstr import Op
brk = pudb.set_trace

def get_key(k):
     return (k.k.func, k.k.var)

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
                if pos in r.comparisons:
                    val = get_regex_choice(r.comparisons[pos])
                    hkey.append(str(val))
                else:
                    # likely input returned without parsing the rest
                    continue
            newk = g.NTKey(k.k.newV(u.h1(':'.join(hkey))))
        comparison_map[k] = newk
    return comparison_map

def get_regex_choice(cmps):
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
    v = g.Choice(g.Box(success_eq), g.Not(g.Box(failure_eq)))
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
        eltregex = get_regex_choice(rule.comparisons[pos])
        regex.append(eltregex)
    return regex

def rule_elts_to_comparisons(rule, tree, comparison_map, nassigns):
    """
    The idea here is to shift away from individual results
    to the comparisons made.
    """
    rvalues = []
    for elt in rule.rvalues():
        if type(elt) is g.NTKey:
            rvalues.append(strip_suffix(key_add_cmp_hash(elt, comparison_map), nassigns))
        else:
            if config.With_Char_Class:
                new_elt = normalize_char_cmp(elt, rule)
            else:
                new_elt = elt
            rvalues.append(new_elt)
    return rule.to_rwrap(rvalues)

def merge_grammars(g1, nlg):
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


def separate_comparisons_per_char(cmps):
    outputs = {}
    for i,o in enumerate(cmps):
        op = o.op_A.x()
        if op not in outputs: outputs[op] = []
        for oc in o.expand():
            outputs[op].append((oc, i))
    return outputs

def process_comparisons_per_char(ins):
    lst = sorted(ins.keys())
    vals = []
    for pos in lst:
        # v is a list of trace ops for position pos
        v = ins[pos]
        vals.append(process_one_instruction(pos, v))
    return vals

def key_add_cmp_hash(elt, comparison_map):
    return comparison_map[elt]

def strip_suffix(elt, nassigns):
    if config.Infer == 'SOUND':
        return elt
    elif is_single_assigned(elt, nassigns):
        # Was the variable assigned to multiple times in the same iteration?
        # if not, it is a strong sign that it is unambiguous as to the part
        # it parses.
        return strip_key_suffix(elt)
    else:
        # multiply assigned. We have no guarantee which part of input it handles
        return elt

def strip_key_suffix(v):
    return g.NTKey(v.k.newV('0'))

def is_leaf(n, tree):
    if not n in tree: return True
    return False

def is_single_assigned(n, nassigns):
    return nassigns[get_key(n)] == 0

def recover_grammar(root, tree, inp, i, xins, nassigns):
    xcmps = process_comparisons_per_char(separate_comparisons_per_char(xins))
    comparison_map = get_regex_map(tree, xcmps, i)
    nodes = [root]
    grammar = {}
    seen = set()
    while nodes:
        n, *nodes = nodes
        if not is_leaf(n, tree):
            rules = tree[n]
            if isinstance(n, g.NTKey):
                key = strip_suffix(key_add_cmp_hash(n, comparison_map), nassigns)
            else:
                if config.With_Char_Class:
                    key = comparison_map[n]
                else:
                    key = key
            # append if more children
            if key not in grammar: grammar[key] = set()
            for rule in rules:
                grammar[key].add(rule_elts_to_comparisons(rule, tree, comparison_map, nassigns))
                nodes.extend(rule.rvalues())
    print(u.readable_grammar(grammar), file=sys.stderr, flush=True)
    print('', file=sys.stderr, flush=True)
    return grammar

def to_context_free(i,tree, nassigns):
    (inp, xins, tree) = tree
    start = g.NTKey(g.V.start())
    return (inp, recover_grammar(start, tree._dict, inp, i, xins, nassigns))

# Get a grammar for multiple inputs
def infer_grammar(parse_trees):
    merged_grammar = g.Grammar()

    # find the maxiumum number of assignments for a named var
    num_assigns = {}
    for (i, cmp, parse_tree) in parse_trees:
        for k in parse_tree._dict:
            key = get_key(k)
            it = int(k.k.t)
            if not key in num_assigns or num_assigns[key] < it:
                num_assigns[key] = it

    comparison_grammar = [to_context_free(i,t, num_assigns) for i,t in enumerate(parse_trees)]
    for j, (i, cmp_tree) in enumerate(comparison_grammar):
        # this is for a single input
        merged_grammar = merge_grammars(merged_grammar, g.Grammar(cmp_tree))
    return merged_grammar
