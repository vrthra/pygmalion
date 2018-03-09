#!/usr/bin/env python3
import pickle
import sys
import jsonpickle
with open(sys.argv[1],"rb") as tf:
    try:
        while True:
            traces = pickle.load(tf)
            frozen = jsonpickle.encode(traces)
            print(frozen)
    except:
        pass
