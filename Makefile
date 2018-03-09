python3=PYTHONPATH=. python3
required_dirs=.pickled
mytargets=hello whilescope microjson
.precious: $(addprefix .pickled/, $(addsuffix .py.trace,$(mytargets)) )

all:


.pickled/%.py.trace: tests/%.py | .pickled
	$(python3) ./bin/traceit.py $<


trace.%: .pickled/%.py.trace
	@echo done

$(required_dirs):; mkdir -p $@

clobber:; rm -rf .pickled


typecheck:
	$(python3) -m mypy --strict --follow-imports=skip -m induce.ftrace
