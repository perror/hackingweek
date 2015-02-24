   HackingWeek: A Django-based Open-source Security Contest Engine
===============================================================

This code is the web engine to run the HackingWeek security contest.

Work in progress...


1. Installing Pinax
-------------------

    $> virtualenv pinax
    $> cd pinax
    $> . bin/activate
    $> git clone https://github.com/perror/hackingweek.git
    $> cd hackingweek
    $> pip install -r config/requirements.pip
    $> ./manage.py syncdb
    $> ./manage.py runserver


2. Generate the locals
----------------------

    $> django-admin.py makemessages --locale=fr
    $> django-admin.py compilemessages --locale=fr


3. Running the tests and code coverage
--------------------------------------

Running the tests:

    $> ./manage.py test [--verbosity=3]

Code coverage with `coverage.py`:

    $> coverage run --source='.' manage.py test
    $> coverage report

To get a full HTML coverage report:

    $> coverage html
    $> iceweasel htmlcov/index.html

HTML validation:

- Go to `https://github.com/validator/validator/releases/latest`.
- Get the last release of `vnu.jar`.
- Install it at `contrib/vnu.jar` at project root.
  (or change the `HTMLVALIDATOR_VNU_JAR` variable in settings.py accordingly).
