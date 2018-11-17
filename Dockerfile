FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /

WORKDIR /

RUN pip install -r ./requirements.txt --no-cache-dir

COPY app/ /app/

WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PRODUCTION_DB_USER=nikolaos
ENV PRODUCTION_DB_PORT=3306
ENV PRODUCTION_DB_NAME=phs_db
CMD flask db upgrade && flask run -h 0.0.0.0 -p 5000
