# ./bin/limits.py
python3=python3
pip3=pip3
required_dirs=.pickled
mytargets=hello whilescope microjson array urljava urlpy mathexpr math expr

.SUFFIXES:

scala=$(addprefix .pickled/, $(addsuffix .scala,$(mytargets)) )
bnf=$(addprefix .pickled/, $(addsuffix .py.bnf,$(mytargets)) )

eval=$(addprefix .pickled/, $(addsuffix .py.eval,$(mytargets)) )
fuzz=$(addprefix .pickled/, $(addsuffix .py.fuzz,$(mytargets)) )
chains=$(addprefix .pickled/, $(addsuffix .py.chain,$(mytargets)) )
traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )
tracks=$(addprefix .pickled/, $(addsuffix .py.track,$(mytargets)) )
mines=$(addprefix .pickled/, $(addsuffix .py.mine,$(mytargets)) )
infers=$(addprefix .pickled/, $(addsuffix .py.infer,$(mytargets)) )
refined=$(addprefix .pickled/, $(addsuffix .py.refine,$(mytargets)) )

.precious: $(chains) $(traces) $(tracks) $(mines) $(infers) $(refined) $(fuzz) $(eval) $(scala) $(bnf)

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

.pickled/%.py.bnf: .pickled/%.py.refine
	$(python3) ./bin/bnf.py $< > $@

chain.%: .pickled/%.py.chain; @:

trace.%: .pickled/%.py.trace; @:

track.%: .pickled/%.py.track; @:

mine.%: .pickled/%.py.mine; @:

infer.%: .pickled/%.py.infer; @:

refine.%: .pickled/%.py.refine; @:

fuzz.%: .pickled/%.py.fuzz; @:

eval.%: .pickled/%.py.eval; @:

scala.%: .pickled/%.scala; @:

bnf.%: .pickled/%.py.bnf; @:

tribble.%: .pickled/%.scala; @:
	java -Xss1g -jar ./bin/gramcov.jar generate --out-dir=gcov --mode=4-path $<

clean.%:
	rm -f .pickled/$(file).$*

cleantill.chain:
	$(MAKE) cleantill.trace
	$(MAKE) clean.chain

cleantill.trace:
	$(MAKE) cleantill.track
	$(MAKE) clean.trace

cleantill.track:
	$(MAKE) cleantill.mine
	$(MAKE) clean.track

cleantill.mine:
	$(MAKE) cleantill.infer
	$(MAKE) clean.mine

cleantill.infer:
	$(MAKE) cleantill.refine
	$(MAKE) clean.infer

cleantill.refine:
	$(MAKE) cleantill.fuzz
	$(MAKE) clean.refine

cleantill.fuzz:
	$(MAKE) cleantill.eval
	$(MAKE) clean.fuzz

cleantill.eval:
	$(MAKE) clean.eval

cleantill.bnf:
	$(MAKE) clean.bnf


xchain.%: from=chain
xchain.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) chain.$*

xtrace.%: from=trace
xtrace.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) trace.$*

xtrack.%: from=track
xtrack.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) track.$*

xmine.%: from=mine
xmine.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) mine.$*

xinfer.%: from=infer
xinfer.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) infer.$*

xrefine.%: from=refine
xrefine.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) refine.$*

xfuzz.%: from=fuzz
xfuzz.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) fuzz.$*

xeval.%: from=eval
xeval.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) eval.$*

xbnf.%: from=bnf
xbnf.%:
	$(MAKE) cleantill.$(from) file=$*.py
	$(MAKE) bnf.$*
	cat .pickled/$*.py.bnf

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

dist=dist/pygmalion.0.1
make dist: req
	rm -rf $(dist);
	mkdir -p $(dist)
	cp -r src $(dist)/
	cp -r pygmalion $(dist)/
	rm -rf $(dist)/*/.git
	rm -rf $(dist)/*/*/.git
	rm -rf $(dist)/.git
	rm -rf $(dist)/src/pip-delete-this-directory.txt
	cp README.md $(dist)/
	cp Makefile $(dist)/
	cp LICENSE $(dist)/
	cp -R bin $(dist)/
	echo "coverage==4.5.1" > $(dist)/requirements.txt
	echo "-e ./src/taintedstr" >> $(dist)/requirements.txt
	echo "-e ./src/pycore" >> $(dist)/requirements.txt
	echo "-e ./src/pychains" >> $(dist)/requirements.txt
	echo "-e ./src/pygfuzz" >> $(dist)/requirements.txt
	cp -R subjects $(dist)/
