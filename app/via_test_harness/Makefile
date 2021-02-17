.PHONY: help
help:
	@echo "make help	Show this help message"
	@echo "make dev		Run the app in the development server"


.PHONY: dev
dev: venv
	@.venv/bin/python app.py

.PHONY: venv
venv: .venv/bin/pip
	@virtualenv .venv -p python3
	@.venv/bin/pip install -r requirements.txt
