#!/usr/bin/env python3

def inputs():
    import sys;
    if len(sys.argv) > 1: return open(sys.argv[1]).readlines()
    return ['1', '234']

def main(s):
    res = []
    while s:
        d,s = s[0], s[1:]
        if not d.in_('0123456789'):
            raise Exception('Error')
        res.append(d)
    return ''.join(res)

if __name__ in '__main__':
    import taintedstr
    for i in inputs():
        print(main(taintedstr.tstr(i)))


