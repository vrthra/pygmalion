#!/usr/bin/env python3

def parse_num(s,i):
    n = ''
    while s[i:] and s[i] == '1':
        n += s[i]
        i = i +1
    return i,n

def parse_paren(s, i):
    assert s[i] == '('
    i, v = parse_expr(s, i+1)
    if s[i:] == '':
        raise Exception(s, i)
    assert s[i] == ')'
    return i+1, v


def parse_expr(s, i = 0):
    expr = []
    while s[i:]:
        c = s[i]
        if c == '1':
            i,n = parse_num(s,i)
            expr.append(n)
        elif c == '+':
            expr.append(c)
            i = i + 1
        elif c == '(':
            i, v = parse_paren(s, i)
            expr.append(v)
        elif c == ')':
            return i, expr
        else:
            raise Exception(s,i)
    return i, expr

def parse(s):
    i,e = parse_expr(s, 0)
    if s[i:]:
        raise Exception(s)
    return e


def main(s):
    return parse(s)

def inputs():
    return ['((1+1)+1)','1+1+(1+(1+1))','1+(1+1)','(1+1)', '(1)', '1']

if __name__ in ['__main__']:
    import taintedstr
    import sys
    if len(sys.argv) == 1:
        for i in inputs():
            print(main(taintedstr.tstr(i)))
    else:
        print(main(taintedstr.tstr(sys.argv[1])))
