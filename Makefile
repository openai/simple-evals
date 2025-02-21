.PHONY: list-models
list-models:
	PYTHONPATH=$$(pwd) python simple_evals.py --list-models


.PHONY: eval-model
eval-model:
	PYTHONPATH=$$(pwd) python simple_evals.py --model $(model) --examples $(n)

