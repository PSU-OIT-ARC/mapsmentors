.PHONY: init clean recreate-db run test coverage

.DEFAULT_GOAL := run

PROJECT_NAME = mentor
VENV_DIR ?= .env
export PATH := $(VENV_DIR)/bin:$(PATH)
MANAGE = ./manage.py

# completely wipes out the database and environment and rebuilds it and loads some dummy data
init: $(VENV_DIR)
	mysql -u root -e 'drop database $(PROJECT_NAME);' || true
	mysql -u root -e 'create database $(PROJECT_NAME);'
	@$(MAKE) reload
	$(MANAGE) test


# run all the usual Django stuff to get this project bootstrapped
reload: $(VENV_DIR)
	$(MANAGE) migrate
	$(MANAGE) collectstatic --noinput
	$(MANAGE) loaddata choices
	mkdir -p media
	touch $(PROJECT_NAME)/wsgi.py


# build the virtualenv
$(VENV_DIR):
	virtualenv -p python3.3 $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt


# remove pyc junk
clean:
	find . -iname "*.pyc" -delete
	find . -iname "*.pyo" -delete
	find . -iname "__pycache__" -delete


# run the django web server
host ?= 0.0.0.0
port ?= 8000
run: $(VENV_DIR)
	$(MANAGE) runserver $(host):$(port)


# run the unit tests
# use `make test test=path.to.test` if you want to run a specific test
test: $(VENV_DIR)
	$(MANAGE) test $(test)


# run the unit tests with coverage.
# go to `0.0.0.0:8000/htmlcov/index.html` to view test coverage
coverage: $(VENV_DIR)
	coverage run ./manage.py test $(test)
	coverage html --omit=.env/*

