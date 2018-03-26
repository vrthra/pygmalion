#!/usr/bin/env python3
import sys
import os.path
import pygmalion.track as track
import pickle
import resource
resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)

if __name__ == "__main__":
    fin = sys.stdin.buffer if len(sys.argv) < 2 else open(sys.argv[1], 'rb')
    fout = sys.stdout.buffer if len(sys.argv) < 2 else open("%s.tmp" % sys.argv[1], 'wb')

    o = track.FrameIter(fin)
    tracker = None
    traces = []
    xins = None
    count = 0
    # this is a single input.
    for i in o:
        event = i['event']
        if event in ['start']:
            inp = i['$input']
            print("track:", count, inp, file=sys.stderr, flush=True)
            count += 1
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
