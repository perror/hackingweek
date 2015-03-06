MANAGE = ./manage.py

LOCALESDIR = hackingweek/locale
LOCALES = $(LOCALESDIR)/fr/LC_MESSAGES/django.mo

OMITFLAGS = --omit "*tests*","*migrations*"

.PHONY:	clean coverage help locales run syncdb test test-dbg

all: syncdb run

run: $(LOCALES)
	$(MANAGE) runserver 0.0.0.0:8000

syncdb:
	$(MANAGE) syncdb --noinput
	$(MANAGE) migrate

test:
	$(MANAGE) test

test-dbg:
	$(MANAGE) test --verbosity=3

cover:
	coverage run  $(OMITFLAGS) --source='.' $(MANAGE) test
	coverage html

coverall:
	coverage run --rcfile='templates.coveragerc' $(OMITFLAGS) --source='.' $(MANAGE) test
	DJANGO_SETTINGS_MODULE=hackingweek.settings coverage html --rcfile='templates.coveragerc'

locales:
	cd hackingweek/ && django-admin.py makemessages --locale=fr

$(LOCALESDIR)/fr/LC_MESSAGES/django.mo: $(LOCALESDIR)/fr/LC_MESSAGES/django.po
	cd hackingweek/ && django-admin.py compilemessages --locale=fr

clean:
	@rm -f `find . -name "*.pyc"` .coverage
	@rm -rf htmlcov/

distclean: clean
	@rm -f $(LOCALES)

help:
	@echo "Makefile usage:"
	@echo "  make [all]\tsync and run the server"
	@echo "  make run\trun the server"
	@echo "  make syncdb\tsync the database (and migrate)"
	@echo "  make locales\tgenerate the locale po files"
	@echo "  make test\trun the test suite"
	@echo "  make test-dbg\trun the test suite with high verbosity"
	@echo "  make cover\trun the test suite on .py files with coverage plugin"
	@echo "  make coverall\trun the test suite on all files with coverage plugin"
	@echo "  make clean\tremove unnecessary files"
	@echo "  make help\tdisplay this help"
