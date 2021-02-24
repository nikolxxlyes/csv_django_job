web: gunicorn project.wsgi:application --log-file - --pythonpath 'project,project.project'
worker: celery --workdir project -A project worker
