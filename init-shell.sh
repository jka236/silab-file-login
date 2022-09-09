#!/bin/sh

export FLASK_APP=project
export FLASK_DEBUG=1

VENV=$(dirname "${BASH_SOURCE[0]}")/venv

if [ ! -d "$VENV" ]; then
    echo "Create venv"
    python -m venv ./venv
fi

source ./venv/bin/activate
pip install -r requirements.txt && flask run --host=0.0.0.0 --port=4000