FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./gunicorn_start.sh /code/gunicorn_start.sh
COPY ./app /code/app

CMD ["sh", "gunicorn_start.sh"]
