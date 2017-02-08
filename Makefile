PYTHON := python3

all: cairoshim/context.py

cairoshim/context.py: generate-context.py cairoshim/context.tpl
	$(PYTHON) generate-context.py ~/codes/pycairo/doc/reference/context.rst cairoshim/context.tpl > cairoshim/context.py
