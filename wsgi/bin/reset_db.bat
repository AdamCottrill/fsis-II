REM a little helper script to make clearing the db a little easier
REM first it removes old tables and then rebuild them without effecting users

python manage.py sqlclear fsis2  --settings=main.settings.local  | python manage.py  dbshell --settings=main.settings.local

python manage.py syncdb --settings=main.settings.local