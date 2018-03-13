python3=PYTHONPATH=. python3
required_dirs=.pickled
mytargets=hello whilescope microjson array url

.SUFFIXES:

traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )
tracks=$(addprefix .pickled/, $(addsuffix .py.track,$(mytargets)) )
mines=$(addprefix .pickled/, $(addsuffix .py.i,$(mytargets)) )
refined=$(addprefix .pickled/, $(addsuffix .py.r,$(mytargets)) )

.precious: $(traces) $(tracks) $(mines) $(refined)

all:
	@echo $(traces)


.pickled/%.py.trace: tests/%.py | .pickled
ifeq ($(debug),trace)
	$(python3) -m pudb ./bin/traceit.py $<
else
	@$(python3) ./bin/traceit.py $<
endif
	@mv $@.tmp $@

.pickled/%.py.track: .pickled/%.py.trace
ifeq ($(debug),track)
	$(python3) -m pudb ./bin/trackit.py $<
else
	@$(python3) ./bin/trackit.py $<
endif
	@mv $<.m $@

.pickled/%.py.i: .pickled/%.py.track
ifeq ($(debug),mine)
	$(python3) -m pudb ./bin/mineit.py $<
else
	@$(python3) ./bin/mineit.py $<
endif
	@mv $<.i $@

.pickled/%.py.r: .pickled/%.py.i
ifeq ($(debug),refine)
	$(python3) -m pudb ./bin/refineit.py $<
else
	@$(python3) ./bin/refineit.py $<
endif
	@mv $<.r $@


trace.%: .pickled/%.py.trace
	@echo

track.%: .pickled/%.py.track
	@echo

mine.%: .pickled/%.py.i
	@echo

refine.%: .pickled/%.py.r
	@echo

xtrace.%:
	rm -f .pickled/$*.py.trace
	$(MAKE) trace.$*

xtrack.%:
	rm -f .pickled/$*.py.track
	$(MAKE) track.$*

xmine.%:
	rm -f .pickled/$*.py.i
	$(MAKE) mine.$*

xrefine.%:
	rm -f .pickled/$*.py.r
	$(MAKE) refine.$*


$(required_dirs):; @mkdir -p $@

clobber:; rm -rf .pickled


typecheck:
	$(python3) -m mypy --strict --follow-imports=skip -m induce.ftrace
