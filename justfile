set export

default:
  just --list

run:
    . .venv/bin/activate
    open-api-maker --input test_files/swagger.yaml --output test_files/openapi.yaml

test:
    . .venv/bin/activate
    pytest

build-and-upload: build upload

build:
    rm -rf dist
    . .venv/bin/activate
    python3 -m build

upload:
    . .venv/bin/activate
    twine upload dist/* --verbose

install-self:
    . .venv/bin/activate
    pip install -e .

init-venv:
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
