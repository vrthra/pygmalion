# Pygmalion

## Requirements

Pygmalion dependes on a number of packages, all of which can be installed using
the following command

```bash
$ make req
```

Note that we have strict requirements for Python. That is, this is tested only
on Python 3.6.5 It _may_ work on later versions, but _will not_ work on
previous versions because we rely on constructs introduced in _3.6_.


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

## Complete end to end for subject _hello.py_

### First generate inputs, derive and evaluate our grammar

```bash
$ make xeval.hello
```

### Next, get the human readable grammar

```bash
$ make xbnf.hello
```

## Stages

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
   point, we nolonger can distinguish separate inputs.
* _refine_
   Try to produce human readable grammar
* _fuzz_
   Generate output from the infered and refined grammar.
* _eval_
   Use the outputs generated and find how many are valid, and the amount of
   coverage obtained

* _bnf_
  This is not a stage for grammar evaluation, but can be used to generate
  Human readable grammars from the refined grammar (depends on _refine_)

Each stage can be invoked by _x<stagename>.<subject>_. For example, for
complete evaluation of _microjson.py_, the following command would be used

```bash
$ make xeval.microjson
```

On the other hand, if only the human readable grammar is neceassary, the
following command is used

```bash
$ make xbnf.microjson
```

## Generating initial inputs using PyChains

The following command generates the initial inputs using PyChains for
_hello.py_

```bash
$ make xchain.hello
```

The result is placed in _.pickled/hello.py.chain_ and can be converted
to readable ASCII by

```bash
$ ./bin/showpickle.py .pickled/hello.py.chain
```

A number of environment variables are used to control the Pygmalion

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

* **NOCTRL**
   Whether to produce characters such as _\t\b\f\x012_ which are not part of
   the list _string.ascii_letters + string.digits + string.punctuation_

* **NO\_LOG** (*1*)
  If set to `0`, we get more informative and verbose output (which slows down
  the program quite a bit).

* **python3**
   The python interpreter used

* **pip3**
   The pip installer command

The configuration can be finetuned further by modifing these `pygmalion.confg`
variables and `pychains.config` variables

### Pygmalion config variables

* *config.Track\_Params* (*True*)
  Whether to track function parameters or not 

* *config.Track\_Vars* (*True*)
  Whether to track local variables or not 

* *config.Track\_Return* (*False*)
  Should we insert a special *return* variable from each function?

* *config.Ignore\_Lambda* (*True*)
  Strip out noise from _lambda_ expressions

* *config.Swap\_Eclipsing_keys* (*True*)
  When we find a smaller key already contains a chunk (usually a _peek_)
  of a later variable, what should we do with the smaller variable? With
  enabled, we simply swap the order of these two variables in causality

* *config.Strip\_Peek* (*True*)
  Related to above -- If we detect a swap, rather than swap, simply discard
  the smaller (earlier) variable.

* *config.Prevent\_Deep\_Stack\_Modification* (*False*)
  Only replace things at a lower height with something at higher height.
  It is useful mainly for returned values that may be smaller than an earlier
  variable deeper in the call scope.

### Pychain config variables

* *config.Wide\_Trigger* (*10*)
  Trigger wide search when this number of similar comparisons is done
  consecutively

* *config.Deep\_Trigger* (*10*)
  Trigger deep search when this number of unique states is reached for wide
  search.

## Examples

### Our evaluations were using these command lines.

```
make xeval.urljava MY_RP=0.1 NINPUT=100 NOUT=1000
make xeval.mathexpr MY_RP=0.1 NINPUT=100 NOUT=1000
make xeval.microjson NINPUT=100 NOUT=1000
```

### Example: Math expression with return probability set to 0.1

```
make xeval.mathexpr MY_RP=0.1
```

### Example: Microjson with logging set.

```
make xeval.microjson NO_LOG=0
```

### Example: Print the bnf for URL

```
make xbnf.urljava NINPUT=100
```

