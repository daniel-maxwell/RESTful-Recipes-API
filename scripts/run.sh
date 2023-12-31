#!/bin/sh

set -e

sudo chmod 666 ./app/db.sqlite3

python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
