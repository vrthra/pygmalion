python3=PYTHONPATH=. python3
required_dirs=.pickled
mytargets=hello whilescope microjson array url

.SUFFIXES:

traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )

.precious: $(traces) $(addsuffix .m,$(traces))

all:
	@echo $(traces)


.pickled/%.py.trace: tests/%.py | .pickled
ifdef debug
	$(python3) -m pudb ./bin/traceit.py $<
else
	@$(python3) ./bin/traceit.py $<
endif

.pickled/%.py.trace.m: .pickled/%.py.trace
ifdef debug
	$(python3) -m pudb ./bin/mtraceit.py $<
else
	@$(python3) ./bin/mtraceit.py $<
endif

.pickled/%.py.trace.m.i: .pickled/%.py.trace.m
ifdef debug
	$(python3) -m pudb ./bin/inferit.py $<
else
	@$(python3) ./bin/inferit.py $<
endif

trace.%: .pickled/%.py.trace
	@echo

mtrace.%: .pickled/%.py.trace.m
	@echo

infer.%: .pickled/%.py.trace.m.i
	@echo


$(required_dirs):; @mkdir -p $@

clobber:; rm -rf .pickled


typecheck:
	$(python3) -m mypy --strict --follow-imports=skip -m induce.ftrace
