REM a little helper script to make clearing the remote db a little easier
REM first it removes old tables and then rebuild them without effecting users
REM requires setting file: deploy2django.py with appropriate db connections

python manage.py sqlclear fsis2  --settings=main.settings.deploy2django  | python manage.py  dbshell --settings=main.settings.deploy2django

python manage.py syncdb --settings=main.settings.deploy2django