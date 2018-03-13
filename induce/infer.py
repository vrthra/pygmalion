import induce.grammar as g

def merge_grammars(g1, g2):
    return g.Grammar({key: g1[key] | g2[key] for key in g1.keys() + g2.keys()})

# Get a grammar for multiple inputs
def infer_grammar(lgrammars):
    merged_grammar = g.Grammar()
    for i, lgrammar in lgrammars:
        merged_grammar = merge_grammars(merged_grammar, lgrammar)
    return merged_grammar
