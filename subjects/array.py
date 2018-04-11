#!/usr/bin/env python3
# An example where there is more to generation than fixing the last char
# the mezzanine validation of equal closing brackets.

def inputs():
    import sys;
    if len(sys.argv) > 1: return open(sys.argv[1]).readlines()
    return ['(1)',
            '(1(2))',
            '(1(2)3)',
            '((12)3)',
            '(((1)2)3)',
            ]


def parens(xs):
    stack = [[]]
    while True:
        x, xs = xs[0], xs[1:]
        if x == '(':
            stack[-1].append([])
            stack.append(stack[-1][-1])
        elif x == ')':
            stack.pop()
            if not stack:
                raise Exception('error: opening bracket is missing')
                #raise ValueError('error: opening bracket is missing')
        elif x.in_('0123456789'):
            stack[-1].append(x)
        else:
            raise Exception('error: Only numbers')
        if xs == '':
            break
    if len(stack) > 1:
        raise Exception('error: closing bracket is missing')
        #raise ValueError('error: closing bracket is missing')
    return stack.pop()

def main(s):
    return parens(s)

if __name__ == '__main__':
    import taintedstr
    for i in inputs():
        print(main(taintedstr.tstr(i)))
