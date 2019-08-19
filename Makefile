.PHONY setup
setup:
	python3 -m virtualenv venv
	source venv/bin/activate

.PHONY install
install:
	pip install -r requirements.txt

.PHONY test
test:
	pytest tests
