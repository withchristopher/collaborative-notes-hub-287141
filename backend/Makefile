SHELL := /bin/bash

.PHONY: help build run stop logs

help:
\t@echo "Targets:"
\t@echo "  build  - Build backend docker image"
\t@echo "  run    - Run backend container (detached)"
\t@echo "  stop   - Stop backend container"
\t@echo "  logs   - Tail backend container logs"

build:
\tdocker build -t collaborative-notes-hub-backend:dev .

run:
\tdocker run -d --rm -p 8000:8000 --name collaborative-notes-hub-backend collaborative-notes-hub-backend:dev

stop:
\t- docker stop collaborative-notes-hub-backend

logs:
\tdocker logs -f collaborative-notes-hub-backend
