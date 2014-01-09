deps:
	pip install -r config/requirements.pip

run:
	./manage.py runserver 0.0.0.0:8000

db:
	./manage.py syncdb --noinput
