
```
$ time make xfuzz.mathexpr INFER=COMPLETE DUMB_SEARCH=1 NO_LOG=1
395.75s user 5.07s system 99% cpu 6:41.53 total
$ make xeval.mathexpr INFER=COMPLETE DUMB_SEARCH=1 NO_LOG=1
62.0% coverage Valid: 81/100
```

```
$ make xfuzz.mathexpr INFER=LOSSY DUMB_SEARCH=1 NO_LOG=1
143,19s user 5,06s system 99% cpu 2:29,05 total
$ make xfuzz.mathexpr INFER=LOSSY DUMB_SEARCH=1 NO_LOG=0
201,59s user 1,43s system 99% cpu 3:24,45 total
67.3% coverage Valid: 4/1000
```

```
$ make xeval.mathexpr INFER=COMPLETE NO_LOG=1
2740,15s user 6,20s system 99% cpu 45:50,71 total
61.3% coverage Valid: 80/100
```

```
$ make xeval.microjson NO_LOG=1 INFER=LOSSY NO_LOG=1
69,97s user 1,64s system 99% cpu 1:12,05 total
41.5% coverage Valid: 38/100
$ make xfuzz.microjson NO_LOG=1 NOUT=1000
28,76s user 1,15s system 99% cpu 29,951 total
46.12% coverage Valid: 382/1000
```

```
make xeval.urljava INFER=LOSSY NO_LOG=1 MY_RP=0.1 DUMB_SEARCH=1
1688,61s user 20,98s system 99% cpu 28:35,19 total
56.77% coverage Valid: 61/100
```

```
make xeval.urljava INFER=LOSSY NO_LOG=1 MY_RP=0.1 DUMB_SEARCH=0
326,21s user 18,73s system 99% cpu 5:46,04 total
56.77% Valid: 88/100
```
