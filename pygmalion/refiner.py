import pygmalion.miner as miner
import pygmalion.grammar as g
import pygmalion.config as config
import sys
import os
import pickle
from pygmalion.bc import bc
import pudb; brk = pudb.set_trace

def nt_key_to_s(i):
    v = i.k
    return "[%s:%s]" % (v.func, v.var)

def char_class_process(lststr):
    i = 0
    last = None
    res = []
    plus = '+'
    while i < len(lststr):
        v = lststr[i]
        i = i+1
        if v == '+':
            res.append('['+ '+' + ']')
            continue
        if len(res) == 0:
            res.append(v)
            continue
        if res[-1] == plus:
            if v == res[-2]:
                pass
            else:
                res.append(v)
        else:
            if v == res[-1]:
                res.append(plus)
            else:
                res.append(v)
    return ''.join(res)

def to_str(i):
    if isinstance(i, str):
        return i
    elif isinstance(i, list):
        return ''.join(i)
    else:
        return type(i).__name__ + ':' + str(i)

def refine_grammar(grammar):
    newg = {}
    for key in grammar.keys():
        rules = grammar[key]
        newk = nt_key_to_s(key)
        if newk not in newg:
            newg[newk] = set()
        newr = newg[newk]
        for r in rules:
            #assert r.comparisons
            my_str = []
            skip = False
            for i in r.rvalues():
                if type(i) == miner.NTKey:
                    str_var = nt_key_to_s(i)
                    skip = True
                else:
                    pos = i.x()
                    str_var = str(i)
                my_str.append(str_var)
            rstr = char_class_process(my_str)
            cmps = []
            if not skip and r.comparisons and config.Show_Comparisons:
                c = r.comparisons[pos]
                cmps.extend(["\t"] +
                        [
                         'EQ_y:' + repr(''.join([to_str(i) for i in c['seq']])) if c['seq'] else '',
                         'NE_y:' + repr(''.join([to_str(i) for i in c['sne']])) if c['sne'] else '',
                         'IN_y:' + repr(''.join([to_str(i) for i in c['sin']])) if c['sin'] else '',
                         'NI_y:' + repr(''.join([to_str(i) for i in c['sni']])) if c['sni'] else '',
                         'EQ_X:' + repr(''.join([to_str(i) for i in c['feq']])) if c['feq'] else '',
                         'NE_x:' + repr(''.join([to_str(i) for i in c['fne']])) if c['fne'] else '',
                         'IN_x:' + repr(''.join([to_str(i) for i in c['fin']])) if c['fin'] else '',
                         'NI_x:' + repr(''.join([to_str(i) for i in c['fni']])) if c['fni'] else '',
                         ])
            else:
                pass
                #my_str.extend([''])
            newr.add(rstr + "\t".join(cmps))
    return g.Grammar(newg)

