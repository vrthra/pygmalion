python3=python3
pip3=pip3
required_dirs=.pickled
mytargets=hello whilescope microjson array urljava urlpy mathexpr

.SUFFIXES:

eval=$(addprefix .pickled/, $(addsuffix .py.eval,$(mytargets)) )
fuzz=$(addprefix .pickled/, $(addsuffix .py.fuzz,$(mytargets)) )
chains=$(addprefix .pickled/, $(addsuffix .py.chain,$(mytargets)) )
traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )
tracks=$(addprefix .pickled/, $(addsuffix .py.track,$(mytargets)) )
mines=$(addprefix .pickled/, $(addsuffix .py.mine,$(mytargets)) )
infers=$(addprefix .pickled/, $(addsuffix .py.infer,$(mytargets)) )
refined=$(addprefix .pickled/, $(addsuffix .py.refine,$(mytargets)) )

.precious: $(chains) $(traces) $(tracks) $(mines) $(infers) $(refined) $(fuzz) $(eval)

all:
	@echo  chains $(chains), traces $(traces), tracks $(tracks), mines $(mines), infers $(infers), refined $(refined), fuzz $(fuzz), eval $(eval)

MY_RP=1.0
NINPUT=10
R=0
NOUT=100
MAXSYM=100

.pickled/%.py.chain: subjects/%.py | .pickled
	NOCTRL=1 MY_RP=$(MY_RP) R=$(R) $(python3) ./bin/pychain.py $< $(NINPUT) > $@.tmp
	mv $@.tmp $@

.pickled/%.py.trace: subjects/%.py .pickled/%.py.chain
ifeq ($(debug),trace)
	$(python3) -m pudb ./bin/traceit.py $< .pickled/$*.py.tmp < .pickled/$*.py.chain
else
	$(python3) ./bin/traceit.py $< .pickled/$*.py.tmp < .pickled/$*.py.chain
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
	NOUT=$(NOUT) MAXSYM=$(MAXSYM) $(python3) -m pudb ./bin/fuzzit.py $<
else
	NOUT=$(NOUT) MAXSYM=$(MAXSYM) $(python3) ./bin/fuzzit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.eval: .pickled/%.py.fuzz
ifeq ($(debug),eval)
	$(python3) -m pudb ./bin/eval.py subjects/$*.py $<
else
	$(python3) ./bin/eval.py subjects/$*.py $<
endif
	@mv $<.tmp $@


chain.%: .pickled/%.py.chain; @:

trace.%: .pickled/%.py.trace; @:

track.%: .pickled/%.py.track; @:

mine.%: .pickled/%.py.mine; @:

infer.%: .pickled/%.py.infer; @:

refine.%: .pickled/%.py.refine; @:

fuzz.%: .pickled/%.py.fuzz; @:

eval.%: .pickled/%.py.eval; @:

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

xrefine.%:
	rm -f .pickled/$*.py.refine
	$(MAKE) refine.$*

xfuzz.%:
	rm -f .pickled/$*.py.fuzz
	$(MAKE) fuzz.$*
	$(python3) ./bin/showpickle.py .pickled/$*.py.fuzz

xeval.%:
	rm -f .pickled/$*.py.eval
	$(MAKE) eval.$*
	cat .pickled/$*.py.eval

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
	@echo mine - Linear grammar
	@echo infer - Context Free grammar
	@echo refine - To normalized form
	@echo fuzz - Get fuzzed output from grammar
	@echo eval - Evaluate the fuzzed output


req:
	$(pip3) install -r requirements.txt --user
