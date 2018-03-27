import pygmalion.grammar as g
import pygmalion.config as config
import pygmalion.miner as miner
import pudb
import sys
from taintedstr import Op
brk = pudb.set_trace


def get_regex(cmps):
    # the input structure is a dict where keys are the instruction
    # numbers and each value is a list of secondary instructions in key:o.
    # or summaries in eq, ne, in, ni sne, fne, sni, sin etc.
    # First priority to all equals that succeeded
    # This is because we should be able to get a grammar that
    # will include this element.
    success_eq = set()
    failure_eq = set()
    for i in cmps:
        kind, v = cmps[i]['charclass']
        if kind:
            success_eq.update(v)
        else:
            failure_eq.update(v)
    v = "([%s]&[%s])" % (''.join(success_eq), ''.join(failure_eq))
    return v


def merge_grammars(g1, lg, xcmps, inp):
    kvdict = {}
    for k in lg.keys():
        rule = lg[k]
        assert len(rule) == 1
        r = list(rule)[0]
        r.comparisons = {i:xcmps[i] for i in r.taint if i < len(xcmps)}
        r._input = inp
        if k.k == g.V.start():
            newk = k
        else:
            hkey = []
            for pos in r._taint:
                val = get_regex(r.comparisons[pos])
                hkey.append(val)
            newk = miner.NTKey(k.k.newV(':'.join(hkey) + k.k.t))
        kvdict[k] = newk


    nlg = {}
    for k in lg.keys():
        hk = kvdict[k]
        assert hk not in nlg
        rules = lg[k]
        newrules = set()
        for rule in rules:
            new_rule = []
            for elt in rule:
                newelt = None
                if type(elt) == miner.NTKey:
                    newk = kvdict[elt]
                    newelt = newk
                else:
                    newelt = elt
                new_rule.append(newelt)
            newr = miner.RWrap(rule.k, new_rule, rule.taint, rule.comparisons)
            newrules.add(newr)
        nlg[hk] = newrules
    nlg = g.Grammar(nlg)
    my_g = {}
    for key in g1.keys() + nlg.keys():
        v = g1[key] | nlg[key]
        my_g[key] = v
    return g.Grammar(my_g)
    # return g.Grammar({key: g1[key] | lg[key] for key in g1.keys() + lg.keys()})

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
        # After the last tainted string update, some of these
        # should go away. Hence the asserts
        eq =  [i for i in v if Op(i.op) == Op.EQ]
        ne =  [i for i in v if Op(i.op) == Op.NE]
        inv = [i for i in v if Op(i.op) == Op.IN]
        nin = [i for i in v if Op(i.op) == Op.NOT_IN]
        assert not nin

        # success
        seq = [i.opB for i in eq if i.opA == i.opB]
        feq = [i.opB for i in eq if i.opA != i.opB]

        sne = [i.opB for i in ne if i.opA != i.opB]
        fne = [i.opB for i in ne if i.opA == i.opB]

        sin = [i.opB for i in inv if i.opA in i.opB]
        fin = [i.opB for i in inv if i.opA not in i.opB]

        sni = [i.opB for i in nin if i.opA not in i.opB]
        fni = [i.opB for i in nin if i.opA in i.opB]

        all_eq = seq + fne
        all_ne = sne + feq

        all_in = sin + fni
        all_ni = sni + fin
        return {'pos':pos, 'opA':opA, \
                'eq': all_eq, 'ne': all_ne, \
                'in': all_in, 'ni': all_ni, \
                'seq': seq, 'feq': feq, \
                'sne':sne, 'fne':fne, \
                'sin':sin, 'fin':fin, \
                'sni':sni, 'fni':fni, 'o':v}

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

# Get a grammar for multiple inputs
def infer_grammar(lgrammars):
    merged_grammar = g.Grammar()
    for j, (i, xins, lgrammar) in enumerate(lgrammars):
        print("infer:", j, i, file=sys.stderr, flush=True)
        # this is for a single input
        xcmps = process_comparisons_per_char(separate_comparisons_per_char(xins))
        merged_grammar = merge_grammars(merged_grammar, lgrammar, xcmps, i)
    return merged_grammar
