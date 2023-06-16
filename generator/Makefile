q: autoflake isort black flake8

autoflake: args ?= .
autoflake:
	poetry run autoflake -r -i --remove-all-unused-imports --remove-unused-variables .

isort: args ?= .
isort:
	poetry run isort .

black: args ?= .
black:
	poetry run black .

flake8: args ?= .
flake8:
	poetry run flake8 .
