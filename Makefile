PYTHON := python3

all: cairoshim/context.py cairoshim/surfaces.py

cairoshim/context.py: generate-shim.py
	$(PYTHON) generate-shim.py ~/codes/pycairo/doc/reference/context.rst cairo > cairoshim/context.py

cairoshim/surfaces.py: generate-shim.py
	$(PYTHON) generate-shim.py ~/codes/pycairo/doc/reference/surfaces.rst cairo > cairoshim/surfaces.py
