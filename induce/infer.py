import induce.grammar as g

def merge_grammars(g1, g2, cmps):
    return g.Grammar({key: g1[key] | g2[key] for key in g1.keys() + g2.keys()})


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
    for i, ins, lgrammar in lgrammars:
        cmps = process_ins(ins)
        merged_grammar = merge_grammars(merged_grammar, lgrammar, cmps)
    return merged_grammar
