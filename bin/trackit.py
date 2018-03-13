#!/usr/bin/env python3
import sys
import os.path
import induce.track as track
import pickle

if __name__ == "__main__":
    o = track.FrameIter(sys.argv[1])
    tracker = None
    traces = []
    # this is a single input.
    for i in o:
        event = i['event']
        if event in ['start']:
            inp, ins = i['$input']
            tracker = track.Tracker(inp, ins)
        elif event in ['stop']:
            traces.append((tracker.vars.i, tracker.vars.ins, tracker.vars.defs))
        else:
            tracker.track(i)
    pickle.dump(traces, open("%s.tmp" % sys.argv[1], "wb" ))
