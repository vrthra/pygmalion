#!/usr/bin/env python3

def inputs():
    return ['[1]',
            '[1, 2]',
            '[1, 2, 3]'
            ]

def main(s):
    if s[0] != '[': return
    if s[-1] != ']': return
    vals = s[1:-1].split(',')
    nums = []
    for v in vals:
        num = v.strip()
        nums.append(num)

if __name__ == '__main__':
    import taintedstr
    for i in inputs():
        print(main(taintedstr.tstr(i)))
