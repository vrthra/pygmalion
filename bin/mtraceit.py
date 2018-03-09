#!/usr/bin/env python3
import sys
import os.path
import induce.mtrace as mtracer
import pickle

if __name__ == "__main__":
    o = mtracer.FrameIter(sys.argv[1])
    tracker = None
    traces = []
    # this is a single input.
    for i in o:
        event = i['event']
        if event in ['start']:
            tracker = mtracer.Tracker(i['$input'])
        elif event in ['stop']:
            traces.append((tracker.vars.i, tracker.vars.defs))
        else:
            tracker.track(i)
    pickle.dump(traces, open("%s.m" % sys.argv[1], "wb" ))
