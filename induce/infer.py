import induce.grammar as g
import pudb
from trackingvm.vm import TraceOp, Op
brk = pudb.set_trace

def merge_grammars(g1, lg, xcmps):
    for k in lg.keys():
        rule = lg[k]
        assert len(rule) == 1
        r = list(rule)[0]
        r.comparisons = {i:xcmps[i] for i in r.taint if i < len(xcmps)}
        # get rule taints.
        pass
    return g.Grammar({key: g1[key] | lg[key] for key in g1.keys() + lg.keys()})

def process_one(pos, v):
    opA = set(i.opA for i in v)
    # EQ
    eq = [i for i in v if Op(i.opnum) == Op.EQ]
    ne = [i for i in v if Op(i.opnum) == Op.NE]
    inv = [i for i in v if Op(i.opnum) == Op.IN]
    nin = [i for i in v if Op(i.opnum) == Op.NOT_IN]

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

    return {'i':pos, 'o':list(opA)[0], 'eq': all_eq, 'ne': all_ne, 'in': all_in, 'ni': all_ni, 'seq': seq, 'feq': feq, 'sne':sne, 'fne':fne, 'sin':sin, 'fin':fin, 'sni':sni, 'fni':fni}

    # belongs_to = seq
    # belongs_to.extend(fne)
    # for i in sin:
    #     belongs_to.extend(i)
    # for i in fni:
    #     belongs_to.extend(i)

    # not_belongs = feq
    # not_belongs.extend(sne)
    # for i in fin:
    #     not_belongs.extend(i)
    # for i in sni:
    #     not_belongs.extend(i)

    # v1 = ''.join(belongs_to)
    # v2 = ''.join(not_belongs)

def process_xins(ins):
    lst = sorted(ins.keys())
    vals = []
    for pos in lst:
        # v is a list of trace ops for position pos
        v = ins[pos]
        vals.append(process_one(pos, v))
    return vals

def process_ins(ins):
    imap = {}
    for i in ins:
        pos, cmp_type, _cwith, cto = i
        if pos not in imap: imap[pos] = []
        imap[pos].append((cmp_type, _cwith, cto))
    return imap

# Get a grammar for multiple inputs
def infer_grammar(lgrammars):
    merged_grammar = g.Grammar()
    for i, xins, lgrammar in lgrammars:
        print(i)
        # this is for a single input
        xcmps = process_xins(xins)
        merged_grammar = merge_grammars(merged_grammar, lgrammar, xcmps)
    return merged_grammar
