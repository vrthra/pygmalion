#!/usr/bin/env python3
# Use a grammar to fuzz, using derivation trees

import random
import pygmalion.miner as miner
import pygmalion.grammar as g
import pygmalion.refiner as refiner
import re
import sys
import json
import pudb
brk = pudb.set_trace
import string
All_Characters = string.ascii_letters + string.digits + string.punctuation


# A regular expression matching the nonterminals used in this grammar
RE_NONTERMINAL = re.compile(r'(\$[a-zA-Z_]*)')

# For debugging:
DEBUG = False
def log(s):
    if DEBUG:
        print(s() if callable(s) else s, file=sys.stderr, flush=True)


# cache the function calls. We only cache a given call based on the
# indicated argument number per function.
def memoize(argnum):
    def fn_wrap(function):
        memo = {}
        def wrapper(*args):
            if args[argnum] in memo: return memo[args[argnum]]
            rv = function(*args)
            memo[args[argnum]] = rv
            return rv
        return wrapper
    return fn_wrap

# The minimum cost of expansion of this symbol
@memoize(0) # memoize on the first arg
def symbol_min_cost(nt, grammar, seen=set()):
    expansions = grammar[nt]
    return min(min_expansions(e, grammar, seen | {nt}) for e in expansions)

# The minimum cost of expansion of this rule
@memoize(0)
def min_expansions(expansion, grammar, seen=set()):
    ex = expansion.rvalues()
    #log("minexpansions %s" % expansion)
    symbols  = [s for s in ex if is_symbol(s)]
    # at least one expansion has no variable to expand.
    if not symbols: return 1

    # if a variable present in the expansion is already in the stack, then it is
    # recursion
    if any(s in seen for s in symbols): return float('inf')
    # the value of a expansion is the sum of all expandable variables inside + 1
    cost = sum(symbol_min_cost(s, grammar, seen) for s in symbols) + 1
    #log("cost = %d" % cost)
    return cost


# We create a derivation tree with nodes in the form (SYMBOL, CHILDREN)
# where SYMBOL is either a nonterminal or terminal,
# and CHILDREN is 
# - a list of children (for nonterminals)
# - an empty list for terminals
# - None for nonterminals that are yet to be expanded
# Example:
# ("$START", None) - the initial tree with just the root node
# ("$START", [("$EXPR", None)]) - expanded once into $START -> $EXPR
# ("$START", [("$EXPR", [("$EXPR", None]), (" + ", []]), ("$TERM", None])]) -
#     expanded into $START -> $EXPR -> $EXPR + $TERM

# Return an initialized tree
def init_tree():
    start_symbol = miner.NTKey(g.V.start())#"[:START]"
    return (start_symbol, None)

def is_symbol(s):
    if type(s) != miner.NTKey: return False
    if s == '+': return False
    return True
    
# Convert an expansion rule to children
@memoize(0)
def expansion_to_children(expansion):
    ex = expansion.rvalues()
    log("Converting " + repr(ex))
    # strings contains all substrings -- both terminals and non-terminals such
    # that ''.join(strings) == expansion
    r = [(s, None) if is_symbol(s) else (s, []) for s in ex if s]
    return r
    
# Expand a node
def expand_node(node, grammar, prefer_shortest_expansion):
    (symbol, children) = node
    log("Expanding " + repr(symbol))
    assert children is None
    
    # Fetch the possible expansions from grammar...
    expansions = grammar[symbol]

    possible_children_with_len = []
    for expansion in expansions:
        a = expansion_to_children(expansion)
        b = min_expansions(expansion, grammar, {symbol})
        possible_children_with_len.append((a, b))
    log('Expanding.1')
    min_len = min(s[1] for s in possible_children_with_len)
    
    # ...as well as the shortest ones
    shortest_children = [child for (child, clen) in possible_children_with_len
                               if clen == min_len]
    
    log('Expanding.2')
    # Pick a child randomly
    if prefer_shortest_expansion:
        children = random.choice(shortest_children)
    else:
        # TODO: Consider preferring children not expanded yet, 
        # and other forms of grammar coverage (or code coverage)
        children, _ = random.choice(possible_children_with_len)

    # Return with a new list
    return (symbol, children)
    
# Count possible expansions - 
# that is, the number of (SYMBOL, None) nodes in the tree
def possible_expansions(tree):
    (symbol, children) = tree
    if children is None:
        return 1

    number_of_expansions = sum(possible_expansions(c) for c in children)
    return number_of_expansions

# short circuit. any will return for the first item that is true without
# evaluating the rest.
def any_possible_expansions(tree):
    (symbol, children) = tree
    if children is None: return True

    return any(any_possible_expansions(c) for c in children)
    
# Expand the tree once
def expand_tree_once(tree, grammar, prefer_shortest_expansion):
    log('Expand once %s %s' % (prefer_shortest_expansion, tree))
    (symbol, children) = tree
    if children is None:
        # Expand this node
        return expand_node(tree, grammar, prefer_shortest_expansion)

    log("Expanding tree " + repr(tree))

    # Find all children with possible expansions
    expandable_children = [i for (i, c) in enumerate(children) if any_possible_expansions(c)]
    
    # Select a random child
    # TODO: Various heuristics for choosing a child here, 
    # e.g. grammar or code coverage
    child_to_be_expanded = random.choice(expandable_children)
    
    # Expand it
    new_child = expand_tree_once(children[child_to_be_expanded], grammar, prefer_shortest_expansion)

    new_children = (children[:child_to_be_expanded] + 
                    [new_child] +
                    children[child_to_be_expanded + 1:])
    
    new_tree = (symbol, new_children)

    log("Expanding tree " + repr(tree) + " into " + repr(new_tree))

    return new_tree
    
# Keep on applying productions
# We limit production by the number of minimum expansions
# alternate limits (e.g. length of overall string) are possible too
def expand_tree(tree, grammar, max_symbols):
    # Stage 1: Expand until we reach the max number of symbols
    log("Expanding")
    while 0 < possible_expansions(tree) < max_symbols:
        tree = expand_tree_once(tree, grammar, False)
        log(lambda: all_terminals(tree))
        
    # Stage 2: Keep on expanding, but now focus on the shortest expansions
    log("Closing")
    while any_possible_expansions(tree):
        tree = expand_tree_once(tree, grammar, True)
        log(lambda: all_terminals(tree))

    return tree

def to_str(v):
    res = []
    if v == '+': return ''
    if type(v) is miner.NTKey:
        return str(v)
    if type(v) == refiner.Choice:
        if v.a:
            return random.choice(list(v.a.v))
        elif v.b:
            lst = [c for c in All_Characters if c not in v.b.v.v]
            return random.choice(lst)
    elif type(v) == refiner.Box:
        return random.choice(list(v.v))
    elif type(v) == refiner.Not:
        lst = [c for c in All_Characters if c not in v.v.v]
        return random.choice(lst)
    else:
        return str(v)
    
# The tree as a string
def all_terminals(tree):
    (symbol, children) = tree
    if children is None:
        # This is a nonterminal symbol not expanded yet
        return to_str(symbol)
    
    if len(children) == 0:
        # This is a terminal symbol
        return to_str(symbol)
    
    # This is an expanded symbol:
    # Concatenate all terminal symbols from all children
    return ''.join([all_terminals(c) for c in children])

# All together
def produce(grammar, max_symbols = 1000):
    # Create an initial derivation tree
    tree = init_tree()
    log(tree)

    # Expand all nonterminals
    tree = expand_tree(tree, grammar, max_symbols)
    log(tree)
    
    # Return the string
    return all_terminals(tree)

def using(fn):
    with fn as f: yield f

if __name__ == "__main__":
    # The grammar to use
    #js, = [f.read() for f in using(open(sys.argv[1], 'r'))]
    grammar = term_grammar #json.loads(js)
    print(produce(grammar, int(symbols)))
