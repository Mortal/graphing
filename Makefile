PYTHON := python3

all: cairoshim/context.py

cairoshim/context.py: generate-shim.py cairoshim/context.tpl
	$(PYTHON) generate-shim.py ~/codes/pycairo/doc/reference/context.rst cairoshim/context.tpl > cairoshim/context.py
