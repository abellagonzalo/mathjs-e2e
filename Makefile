.PHONY: setup
setup:
	python3 -m virtualenv venv
	@echo "-----------------------------------------"
	@echo "run this command: source venv/bin/activate"
	@echo "-----------------------------------------"

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: test
test:
	pytest tests
