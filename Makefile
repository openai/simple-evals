.PHONY: setup
setup:
	conda activate codex
	pip install -r requirements.txt

.PHONY: list-models
list-models:
	PYTHONPATH=$$(pwd) python simple_evals.py --list-models


.PHONY: eval
eval:
	PYTHONPATH=$$(pwd) python simple_evals.py --model $(model) --examples $(n)


.PHONY: eval-all
eval-all:
	PYTHONPATH=$$(pwd) python simple_evals.py --model $(model)