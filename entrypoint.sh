#!/bin/sh

if [ "$POSTGRES_DB" = "platform" ]
then 
    echo "Ждем postgres..."

    while ! nc -z "db" $POSTGRES_PORT; do
        sleep 0.5
    deployment

    echo "PostgresSQL запущен"
fi


python manage.py makemigrations
python manage.py migrate


# python manage.py loaddata fixtures/clean_full_dump.json

exec "$@"

