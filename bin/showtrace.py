#!/usr/bin/env python3
import sys
sys.path.append('.')
import pickle
import jsonpickle
with open(sys.argv[1],"rb") as tf:
    try:
        while True:
            traces = pickle.load(tf)
            for i in traces:
                print(jsonpickle.encode(i))
    except:
        pass
