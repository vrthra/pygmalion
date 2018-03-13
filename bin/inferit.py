#!/usr/bin/env python3
import induce.infer as infer
import induce.grammar as g
import sys
import pickle

if __name__ == "__main__":
    grammarinfo = pickle.load(open(sys.argv[1], "rb" ))
    grammar = infer.infer_grammar(grammarinfo)
    print(str(grammar))
    pickle.dump(grammar, open("%s.tmp" % sys.argv[1], "wb"))
