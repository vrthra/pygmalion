# Pygmalion

## Requirements

Pygmalion dependes on a number of packages, all of which can be installed using
the following command

```bash
$ make req
```

## Subjects

We have the following subjects under the _./subjects_ directory

* hello.py
* array.py
* microjson.py
* urlpy.py
* urljava.py
* mathexpr.py
* expr.py
* number.py

## Complete end to end.

```bash
$ make xeval.hello
```

We have the following stages

* _chain_
   Generates the initial inputs using _PyChains_
* _trace_
   Runs the generated inputs through a python frame tracer. This is the only
   python specific part. Unfortunately, because we mess with settrace,
   debugging is not available. Hence the next phase is separated out.
* _track_
   Evaluate the dumped frames to assertain scopes and causality rules. We
   essentially retrieve the input stack information from the dumped frames.
* _mine_
   Mine the parse tree from the stack frames. These are still input
   specific (hence the parse tree)
* _infer_
   Generate the context free grammar by merging the parse trees. At this
   point, we nolonger can distinguish separate inputs. If _WITH_CHAR_CLASS_
* _refine_
   Try to produce human readable grammar
* _fuzz_
   Generate output from the infered and refined grammar.
* _eval_
   Use the outputs generated and find how many are valid, and the amount of
   coverage obtained

Each stage can be invoked by _x<stagename>.<subject>_. For example, for
complete evaluation of _microjson.py_, the following command would be used

```bash
$ make xeval.microjson
```

On the other hand, if only production of grammar is neceassary, the following
command is used

```bash
$ make xrefine.microjson
```


## Generating initial inputs using PyChains

The following command generates the initial inputs using PyChains for
_hello.py_

```bash
$ make xchain.hello
```

The result is placed in _.pickled/hello.py.chain_ and is in readable ASCII
A number of environment variables are used to control the Pygmalion

* **BFS**
   Whether to apply the wide search strategy or not. This has the effect of
   finding out closing elements in subjects such as *microjson* and *array*
   but can result in inputs that are shorter in length. Default is *false*

* **MY\_RP**
   Used to indicate how to proceed when an input is accepted. Some subjects such
   as _urlpy.py_ and _urljava.py_ allows single character inputs that should be
   extended to produce larger inputs. Default is *1.0*. Choose **MY_RP=0.1**
   for _urljava.py_ for reasonable URLs


* **NINPUT**
   The number of inputs that the *Chain* should produce before stopping.
   Default is *10*.

* **R**
   The random number seed. The default is *0*.

* **NOCTL**
   Whether to produce characters such as _\t\b\f\x012_ which are not part of
   the list _string.ascii_letters + string.digits + string.punctuation_

* **WIDE\_TRIGGER** (*10*)
   The number of consecutive similar comparisons before *wide-search* strategy
   on pychains is triggered.

* **DEEP\_TRIGGER** (*1000*)
   The number of states that the *wide-search* strategy has to hit before
  *deep-search* strategy is triggered.

* **PYTHON\_OPT**
   Whether to optimize for python specific string comparisons. Normally, the
   _tainted string_ converts all relevant string operations equality comparisons
   on characters. With this variable set, the other comparisons such as
   *NE*, *IN*, *NOT_IN* etc are also used for generation. It is not useful for
   the rest of commands. Hence, if you use it, make sure to generate the chain
   output separately from other commands such as *trace*, *track*, *infer*,
   *refine*, and *fuzz*

* **WITH\_CHAR\_CLASS** (*True*)
  If specified, replaces individual characters with regular expression
  corresponding to comparisons on that index.

* **python3**
   The python interpreter used

* **pip3**
   The pip installer command

The configuration can be finetuned further by modifing these `pygmalion.confg`
vars

* config.Track_Params (*True*)
  Whether to track function parameters or not 

* config.Track_Vars (*True*)
  Whether to track local variables or not 

* config.Track_Return (*False*)
  Should we insert a special *return* variable from each function?

* config.Ignore_Lambda (*True*)
  Strip out noice from _lambda_ expressions

* config.Swap_Eclipsing_keys (*True*)
  When we find a smaller key already contains a chunk (usually a _peek_)
  of a later variable, what should we do with the smaller variable? With
  enabled, we simply swap the order of these two variables in causality

* config.Strip_Peek (*True*)
  Related to above -- If we detect a swap, rather than swap, simply discard
  the smaller (earlier) variable.

* config.Prevent_Deep_Stack_Modification (*False*)
  Only replace things at a lower height with something at higher height.
  It is useful mainly for returned values that may be smaller than an earlier
  variable deeper in the call scope.

* Use_Character_Classes (*True*)
  (* used in _refiner_ hence deprecated*)


## Examples


### Using Dumb Search for pychain and INFER for grammar

```
make xeval.mathexpr INFER=COMPLETE DUMB_SEARCH=1 NO_LOG=1
```

Using INFER=LOSSY here gets really terrible results

```
make xeval.mathexpr INFER=LOSSY DUMB_SEARCH=1 NO_LOG=1
```

### Using Return Probability for pychain

```
make xeval.urljava INFER=LOSSY NO_LOG=1 MY_RP=0.1
```

### Using direct evaluation

```
make xinfer.microjson NO_LOG=1 INFER=LOSSY NOUT=1000
```

