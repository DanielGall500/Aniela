FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src/app /code/app

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "80"]