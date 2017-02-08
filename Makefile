PYTHON := python3
FILES := cairoshim/constants.py cairoshim/context.py cairoshim/exceptions.py cairoshim/index.py cairoshim/matrix.py cairoshim/paths.py cairoshim/patterns.py cairoshim/region.py cairoshim/surfaces.py cairoshim/text.py

all: $(FILES)

$(FILES): cairoshim/%.py: generate-shim.py
	$(PYTHON) generate-shim.py ~/codes/pycairo/doc/reference/$*.rst cairo > $@
