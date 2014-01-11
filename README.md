   HackingWeek: A Django-based Open-source Security Contest Engine
===============================================================

This code is the web engine to run the HackingWeek security contest.

Work in progress...


1. Installing Pinax
-------------------

    $> virtualenv pinax
    $> cd pinax
    $> . bin/activate
    $> cd hackingweek
    $> pip install -r config/requirements.pip
    $> python manage.py syncdb
    $> python manage.py runserver


2. Get the hackingweek code
---------------------------

    git clone git@github.com:perror/hackingweek.git


3. Generate the locals
----------------------

    django-admin.py compilemessages --locale=fr
