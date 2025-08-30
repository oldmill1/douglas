#!/bin/bash
# Douglas wrapper script - activates venv and runs douglas.py
DOUGLAS_DIR="/Users/ataxali/dev/douglas"
source "$DOUGLAS_DIR/.venv/bin/activate"
python3 "$DOUGLAS_DIR/douglas.py" "$@"
