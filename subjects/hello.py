#!/usr/bin/env python3

def inputs():
    import sys;
    if len(sys.argv) > 1: return open(sys.argv[1]).readlines()
    return ['hello', 'HELLO']

def main(s):
    h,s = s[0], s[1:]
    assert h == 'h' or h == 'H'
    assert s != ''
    e,s = s[0], s[1:]
    assert e == 'e' or e == 'E'
    assert s != ''
    l1, s = s[0], s[1:]
    assert l1 == 'l' or l1 == 'L'
    assert s != ''
    l2, s = s[0], s[1:]
    assert l2 == 'l' or l2 == 'L'
    assert s != ''
    o, s = s[0], s[1:]
    assert o == 'o' or o == 'O'
    assert s == ''
    return h + e + l1 + l2 + o

if __name__ in '__main__':
    import taintedstr
    for i in inputs():
        print(main(taintedstr.tstr(i)))


