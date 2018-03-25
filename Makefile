python3=PYTHONPATH=. python3
pip3=pip3
required_dirs=.pickled
mytargets=hello whilescope microjson array urljava urlpy mathexpr

.SUFFIXES:

input=$(addprefix .pickled/, $(addsuffix .py.input,$(mytargets)) )
chains=$(addprefix .pickled/, $(addsuffix .py.chain,$(mytargets)) )
traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )
tracks=$(addprefix .pickled/, $(addsuffix .py.track,$(mytargets)) )
mines=$(addprefix .pickled/, $(addsuffix .py.mine,$(mytargets)) )
infers=$(addprefix .pickled/, $(addsuffix .py.infer,$(mytargets)) )
refined=$(addprefix .pickled/, $(addsuffix .py.refine,$(mytargets)) )

.precious: $(chains) $(traces) $(tracks) $(mines) $(infers) $(refined) $(input)

all:
	@echo  chains $(chains), traces $(traces), tracks $(tracks), mines $(mines), infers $(infers), refined $(refined), input $(input)

MY_RP=1.0
NINPUT=10
R=0

.pickled/%.py.chain: subjects/%.py | .pickled
	NOCTRL=1 MY_RP=$(MY_RP) R=$(R) $(python3) ./bin/pychain.py $< $(NINPUT) > $@.tmp
	mv $@.tmp $@

.pickled/%.py.trace: subjects/%.py .pickled/%.py.chain
ifeq ($(debug),trace)
	$(python3) -m pudb ./bin/traceit.py $< .pickled/$*.py.tmp < .pickled/$*.py.chain
else
	@$(python3) ./bin/traceit.py $< .pickled/$*.py.tmp < .pickled/$*.py.chain
endif
	@mv .pickled/$*.py.tmp $@

.pickled/%.py.track: .pickled/%.py.trace
ifeq ($(debug),track)
	$(python3) -m pudb ./bin/trackit.py $<
else
	@$(python3) ./bin/trackit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.mine: .pickled/%.py.track
ifeq ($(debug),mine)
	$(python3) -m pudb ./bin/mineit.py $<
else
	@$(python3) ./bin/mineit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.infer: .pickled/%.py.mine
ifeq ($(debug),infer)
	$(python3) -m pudb ./bin/inferit.py $<
else
	@$(python3) ./bin/inferit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.refine: .pickled/%.py.infer
ifeq ($(debug),refine)
	$(python3) -m pudb ./bin/refineit.py $<
else
	@$(python3) ./bin/refineit.py $<
endif
	@mv $<.tmp $@

.pickled/%.py.input: .pickled/%.py.refine
ifeq ($(debug),fuzz)
	$(python3) -m pudb ./bin/fuzzit.py $<
else
	@$(python3) ./bin/fuzzit.py $<
endif
	@mv $<.tmp $@


chain.%: .pickled/%.py.chain
	@echo

trace.%: .pickled/%.py.trace
	@echo

track.%: .pickled/%.py.track
	@echo

mine.%: .pickled/%.py.mine
	@echo

infer.%: .pickled/%.py.infer
	@echo

refine.%: .pickled/%.py.refine
	@echo

fuzz.%: .pickled/%.py.input
	@echo


xchain.%:
	rm -f .pickled/$*.py.chain
	@echo
	$(MAKE) chain.$*

xtrace.%:
	rm -f .pickled/$*.py.trace
	@echo
	$(MAKE) trace.$*

xtrack.%:
	rm -f .pickled/$*.py.track
	@echo
	$(MAKE) track.$*

xmine.%:
	rm -f .pickled/$*.py.mine
	@echo
	$(MAKE) mine.$*

xinfer.%:
	rm -f .pickled/$*.py.infer
	@echo
	$(MAKE) infer.$*

xrefine.%:
	rm -f .pickled/$*.py.refine
	@echo
	$(MAKE) refine.$*

xfuzz.%:
	rm -f .pickled/$*.py.input
	@echo
	$(MAKE) fuzz.$*


$(required_dirs):; @mkdir -p $@

clobber:; rm -rf .pickled

clean:; rm -f .pickled/*.chain


typecheck:
	$(python3) -m mypy --strict --follow-imports=skip -m pygmalion.ftrace

help:
	@echo "trace | track | mine | infer | refine"
	@echo trace - Simple frame dumper -- use xtrace.hello
	@echo track - Evaluate the dumps, figure out the causal chain
	@echo mine - Linear grammar
	@echo infer - Context Free grammar
	@echo refine - To normalized form


req:
	$(pip3) install -r requirements.txt --user
