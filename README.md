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
