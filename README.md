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
   Mine the linear grammar from the stack frames. These are still input
   specific (hence the linear grammar)
* _infer_
   Generate the context free grammar by merging the mined grammar. At this
   point, we nolonger can distinguish separate inputs.
* _refine_
   Try to produce human readable grammar
* _fuzz_
   Generate output from the infered and refined grammar.
* _eval_
   Use the outputs generated and find how many are valid, and the amount of
   coverage obtained


## Generating initial inputs using PyChains

The following command generates the initial inputs using PyChains for
_hello.py_

```bash
$ make xchain.hello
```

The result is placed in _.pickled/hello.py.chain_ and is in readable ASCII
A number of environment variables are used to control the PyChains

* **BFS**
   Whether to apply the wide search strategy or not. This has the effect of
   finding out closing elements in subjects such as *microjson* and *array*
   but can result in inputs that are shorter in length. Default is *false*

* **MY_RP**
   Used to indicate how to proceed when an input is accepted. Some subjects such
   as _urlpy.py_ allows single character inputs that can be extended to produce
   larger inputs. Default is *1.0*.

* **NINPUT**
   The number of inputs that the *Chain* should produce before stopping.
   Default is *10*.

* **R**
   The random number seed. The default is *0*.

* **NOCTL**
   Whether to produce characters such as _\t\b\f\x012_ which are not part of
   the list _string.ascii_letters + string.digits + string.punctuation_

* **PYTHON\_OPT**
   Whether to optimize for python specific string comparisons. Normally, the
   _tainted string_ converts all relevant string operations equality comparisons
   on characters. With this variable set, the other comparisons such as
   *NE*, *IN*, *NOT_IN* etc are also used for generation. It is not useful for
   the rest of commands. Hence, if you use it, make sure to generate the chain
   output separately from other commands such as *trace*, *track*, *infer*,
   *refine*, and *fuzz*


* **python3**
   The python interpreter used

* **pip3**
   The pip installer command
