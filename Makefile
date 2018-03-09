python3=PYTHONPATH=. python3
required_dirs=.pickled
mytargets=hello whilescope microjson

.SUFFIXES:

traces=$(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )

.precious: $(traces) $(addsuffix .m,$(traces))

all:
	@echo $(traces)


.pickled/%.py.trace: tests/%.py | .pickled
	@$(python3) ./bin/traceit.py $<

.pickled/%.py.trace.m: .pickled/%.py.trace
	@$(python3) ./bin/mtraceit.py $<

.pickled/%.py.trace.m.i: .pickled/%.py.trace.m
	@$(python3) ./bin/inferit.py $<

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
