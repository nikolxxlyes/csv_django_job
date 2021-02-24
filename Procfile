web: gunicorn project.wsgi:application --log-file - --timeout 10 --max-requests 100 --pythonpath 'project,project.project'
worker: celery --workdir project -A project worker
