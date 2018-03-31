#!/usr/bin/env python3
def E(s):
    s = T(s)
    s = Estar(s)
    return s

def Estar(s): # matches epsilon
    if s == '': return s
    if s[0] == "+" or s[0] == "-":
        s = s[1:]
        s = T(s)
        s = Estar(s)
        return s
    return s

def T(s):
    s = F(s)
    s = Tstar(s)
    return s

def Tstar(s): # matches epsilon
    if s == '': return s
    if s[0] == "*" or s[0] == "/":
        s = s[1:]
        s = F(s)
        s = Tstar(s)
        return s
    return s

def F(s):
    if s[0] == "(":
        s = s[1:]
        s = E(s)
        if s[0] == ")":
            s = s[1:]
        else:
            raise Exception("syntax error")
    elif s[0].in_('0123456789'):
        s = s[1:]
    else:
        raise Exception("syntax error")
    return s

def parse(s):
    s = E(s)
    if s != '':
        raise Exception("syntax error")
    return s

def main(s):
    return parse(s)

def inputs():
    return ['1+(2*3)/4']

if __name__ in ['__main__']:
    import sys
    import taintedstr
    if len(sys.argv) == 0:
        print(main(taintedstr.tstr(sys.argv[1])))
    else:
        for i in inputs():
            v = main(taintedstr.tstr(i))
            print(v)
