#!/bin/bash

# arg 1 ($1) must be the project path (path to venv)

cd "$1" || exit

python3 -m venv venv

source "$1/venv/bin/activate" || exit

pip install --upgrade pip

pip install -r "$1/requirements.txt"