#!/usr/bin/env python3
import pickle
import sys
import jsonpickle
with open(sys.argv[1],"rb") as tf:
    try:
        while True:
            p = pickle.load(tf)
            #print(jsonpickle.encode(p))
            print(p)
    except:
        pass
