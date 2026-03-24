web: python manage.py migrate --noinput && gunicorn App.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 180
