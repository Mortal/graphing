PYTHON := python3

all: cairoshim/context.py cairoshim/surfaces.py

cairoshim/context.py: generate-shim.py cairoshim/context.tpl
	$(PYTHON) generate-shim.py ~/codes/pycairo/doc/reference/context.rst cairoshim/context.tpl > cairoshim/context.py

cairoshim/surfaces.py: generate-shim.py cairoshim/surfaces.tpl
	$(PYTHON) generate-shim.py ~/codes/pycairo/doc/reference/surfaces.rst cairoshim/surfaces.tpl > cairoshim/surfaces.py
