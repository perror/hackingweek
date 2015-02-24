MANAGE = ./manage.py

.PHONY:	clean coverage help locales pofiles run syncdb test test-dbg

all: syncdb run

run:
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
	cd hackingweek/ && django-admin.py compilemessages --locale=fr

pofiles:
	cd hackingweek/ && django-admin.py makemessages --locale=fr

clean:
	rm -f `find . -name "*.pyc"` .coverage
	rm -rf htmlcov/

help:
	@echo "Makefile usage:"
	@echo "  make [all]\tsync and run the server"
	@echo "  make run\trun the server"
	@echo "  make syncdb\tsync the database (and migrate)"
	@echo "  make locales\tcompile the locales"
	@echo "  make pofiles\tgenerate the po files"
	@echo "  make test\trun the test suite"
	@echo "  make test-dbg\trun the test suite with high verbosity"
	@echo "  make coverage\trun the test suite with coverage plugin"
	@echo "  make clean\tremove unnecessary files"
	@echo "  make help\tdisplay this help"
