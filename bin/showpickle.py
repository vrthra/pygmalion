#!/usr/bin/env python3
import pickle
import sys
count = 0
with open(sys.argv[1],"rb") as tf:
    try:
        while True:
            p = pickle.load(tf)
            count += 1
            #print(jsonpickle.encode(p))
            print(p)
    except:
        pass
print(count)
