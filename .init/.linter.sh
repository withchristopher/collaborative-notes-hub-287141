#!/bin/bash
cd /home/kavia/workspace/code-generation/collaborative-notes-hub-287141/backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

