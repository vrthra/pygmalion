python3=PYTHONPATH=. python3
required_dirs=.pickled
mytargets=hello whilescope microjson array url

.SUFFIXES:

traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )
tracks=$(addprefix .pickled/, $(addsuffix .py.track,$(mytargets)) )
infers=$(addprefix .pickled/, $(addsuffix .py.i,$(mytargets)) )

.precious: $(traces) $(tracks) $(infers)

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
ifeq ($(debug),infer)
	$(python3) -m pudb ./bin/inferit.py $<
else
	@$(python3) ./bin/inferit.py $<
endif
	@mv $<.i $@

trace.%: .pickled/%.py.trace
	@echo

track.%: .pickled/%.py.track
	@echo

infer.%: .pickled/%.py.i
	@echo


$(required_dirs):; @mkdir -p $@

clobber:; rm -rf .pickled


typecheck:
	$(python3) -m mypy --strict --follow-imports=skip -m induce.ftrace
