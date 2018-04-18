python3=python3
pip3=pip3
required_dirs=.pickled
mytargets=hello whilescope microjson array urljava urlpy mathexpr math expr

.SUFFIXES:

scala=$(addprefix .pickled/, $(addsuffix .scala,$(mytargets)) )

eval=$(addprefix .pickled/, $(addsuffix .py.eval,$(mytargets)) )
fuzz=$(addprefix .pickled/, $(addsuffix .py.fuzz,$(mytargets)) )
chains=$(addprefix .pickled/, $(addsuffix .py.chain,$(mytargets)) )
traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )
tracks=$(addprefix .pickled/, $(addsuffix .py.track,$(mytargets)) )
mines=$(addprefix .pickled/, $(addsuffix .py.mine,$(mytargets)) )
infers=$(addprefix .pickled/, $(addsuffix .py.infer,$(mytargets)) )
induces=$(addprefix .pickled/, $(addsuffix .py.induce,$(mytargets)) )
refined=$(addprefix .pickled/, $(addsuffix .py.refine,$(mytargets)) )

.precious: $(chains) $(traces) $(tracks) $(mines) $(induces) $(infers) $(refined) $(fuzz) $(eval) $(scala)

all:
	@echo  chains $(chains), traces $(traces), tracks $(tracks), mines $(mines), infers $(infers), refined $(refined), fuzz $(fuzz), eval $(eval)

export MY_RP:=1.0
export R:=0
export NOUT:=100
export MAXSYM=100
export INFER:=COMPLETE
export NOCTRL:=0
export NO_LOG:=1
NINPUT=100

.pickled/%.py.chain: subjects/%.py | .pickled
	$(python3) ./bin/pychain.py $< $(NINPUT) $@.tmp
	mv $@.tmp $@

.pickled/%.py.trace: subjects/%.py .pickled/%.py.chain
ifeq ($(debug),trace)
	$(python3) -m pudb ./bin/traceit.py $< .pickled/$*.py.tmp .pickled/$*.py.chain
else
	$(python3) ./bin/traceit.py $< .pickled/$*.py.tmp .pickled/$*.py.chain
endif
	@mv .pickled/$*.py.tmp $@

.pickled/%.py.track: .pickled/%.py.trace
ifeq ($(debug),track)
	$(python3) -m pudb ./bin/trackit.py $<
else
	$(python3) ./bin/trackit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.mine: .pickled/%.py.track
ifeq ($(debug),mine)
	$(python3) -m pudb ./bin/mineit.py $<
else
	$(python3) ./bin/mineit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.induce: .pickled/%.py.mine
ifeq ($(debug),induce)
	$(python3) -m pudb ./bin/induce.py $<
else
	$(python3) ./bin/induce.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.infer: .pickled/%.py.mine
ifeq ($(debug),infer)
	$(python3) -m pudb ./bin/inferit.py $<
else
	$(python3) ./bin/inferit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.refine: .pickled/%.py.infer
ifeq ($(debug),refine)
	$(python3) -m pudb ./bin/refineit.py $<
else
	$(python3) ./bin/refineit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.fuzz: .pickled/%.py.refine
ifeq ($(debug),fuzz)
	$(python3) -m pudb ./bin/fuzzit.py $<
else
	$(python3) ./bin/fuzzit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.eval: .pickled/%.py.fuzz
ifeq ($(debug),eval)
	$(python3) -m pudb ./bin/eval.py subjects/$*.py $<
else
	$(python3) ./bin/eval.py subjects/$*.py $<
endif
	@mv $<.tmp $@

.pickled/%.scala: .pickled/%.py.refine
	$(python3) ./bin/scala.py $< > $@

chain.%: .pickled/%.py.chain; @:

trace.%: .pickled/%.py.trace; @:

track.%: .pickled/%.py.track; @:

mine.%: .pickled/%.py.mine; @:

infer.%: .pickled/%.py.infer; @:

induce.%: .pickled/%.py.induce; @:

refine.%: .pickled/%.py.refine; @:

fuzz.%: .pickled/%.py.fuzz; @:

eval.%: .pickled/%.py.eval; @:

scala.%: .pickled/%.scala; @:

tribble.%: .pickled/%.scala; @:
	java -Xss1g -jar ./bin/gramcov.jar generate --out-dir=gcov --mode=4-path $<

xchain.%:
	rm -f .pickled/$*.py.chain
	$(MAKE) chain.$*

xtrace.%:
	rm -f .pickled/$*.py.trace
	$(MAKE) trace.$*

xtrack.%:
	rm -f .pickled/$*.py.track
	$(MAKE) track.$*

xmine.%:
	rm -f .pickled/$*.py.mine
	$(MAKE) mine.$*

xinfer.%:
	rm -f .pickled/$*.py.infer
	$(MAKE) infer.$*

xinduce.%:
	rm -f .pickled/$*.py.induce
	$(MAKE) induce.$*

xrefine.%:
	rm -f .pickled/$*.py.refine
	$(MAKE) refine.$*

xfuzz.%:
	rm -f .pickled/$*.py.fuzz
	$(MAKE) fuzz.$*

xeval.%:
	rm -f .pickled/$*.py.eval
	$(MAKE) eval.$*

clobber.%:
	rm -f .pickled/$*.*


$(required_dirs):; @mkdir -p $@

clobber:; rm -rf .pickled

clean:; rm -f .pickled/*.chain


typecheck:
	$(python3) -m mypy --strict --follow-imports=skip -m pygmalion.ftrace

help:
	@echo "chain| trace | track | mine | infer | refine | fuzz | eval"
	@echo chain - Pychains test generator -- use xchain.hello
	@echo trace - Simple frame dumper -- use xtrace.hello
	@echo track - Evaluate the dumps, figure out the causal chain
	@echo mine - Mine parse trees
	@echo infer - Context Free grammar
	@echo refine - To normalized form
	@echo fuzz - Get fuzzed output from grammar
	@echo eval - Evaluate the fuzzed output
	
	@echo scala - Generate the scala grammar for Tribble


req:
	$(python3) -c 'import sys; assert sys.version_info >= (3,6)'
	$(pip3) install -r requirements.txt --user
