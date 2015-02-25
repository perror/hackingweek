MANAGE = ./manage.py

LOCALESDIR = hackingweek/locale
LOCALES = $(LOCALESDIR)/fr/LC_MESSAGES/django.mo


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

coverage:
	coverage run --source='.' $(MANAGE) test
	coverage html

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
	@echo "  make coverage\trun the test suite with coverage plugin"
	@echo "  make clean\tremove unnecessary files"
	@echo "  make help\tdisplay this help"
