.PHONY: lint
lint: black

.PHONY: test
test: install black
	poetry run python -m pytest -v

.PHONY: test-fast
test-fast:
	poetry run python -m pytest -v

.PHONY: install
install:
	poetry install

.PHONY: installpoetry
installpoetry:
	@curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

.PHONY: black
black:
	poetry run black .