.PHONY: list-models
list-models:
	# add current path to python path
	PYTHONPATH=$$(pwd) python3 simple_evals.py --list-models