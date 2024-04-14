#!/bin/sh


python3 manage.py makemigrations backend
echo "makemigrations run"

python3 manage.py migrate  
echo "migrate run"

python manage.py runserver 0.0.0.0:8080  
echo "manage.py runserver 0.0.0.0:8080"
