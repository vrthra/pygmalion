#!/usr/bin/env python3
import sys
import os.path
import pygmalion.track as track
import pickle

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')

    o = track.FrameIter(fin)
    tracker = None
    traces = []
    xins = None
    # this is a single input.
    for i in o:
        event = i['event']
        if event in ['start']:
            inp = i['$input']
            tracker = track.Tracker(inp)
        elif event in ['stop']:
            comparisons = i['$comparisons']
            traces.append((tracker.vars.i, comparisons, tracker.vars.defs))
            if os.getenv('DEBUG'):
                for k in tracker.vars.defs.keys():
                    print(k, file=sys.stderr, flush=True)
                    print("\t",tracker.vars.defs[k], file=sys.stderr, flush=True)
                print()
        else:
            tracker.track(i)
    pickle.dump(traces, fout)
