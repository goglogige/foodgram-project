FROM python:3.8.10

WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
