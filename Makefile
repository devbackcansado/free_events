.PHONY: server worker beat shell migrate build prod

server:
	cd src && python manage.py runserver

prod:
	cd src && granian --interface wsgi core.wsgi:application --port 8000 --host 0.0.0.0 --workers 4 --log-level debug

worker:
	cd src && watchfiles --filter python 'celery -A core.celery_app worker -l INFO'

beat:
	cd src && watchfiles --filter python 'celery -A core.celery_app beat -l INFO'

shell:
	cd src && python manage.py shell_plus

migrate:
	cd src && python manage.py makemigrations && python manage.py migrate

build:
	cd src && python manage.py collectstatic --noinput
