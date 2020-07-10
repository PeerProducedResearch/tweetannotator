release: python manage.py migrate
web: gunicorn twitter_annotator.wsgi:application --log-file -
