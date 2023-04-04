#!/bin/bash

NAME=translate-api
DIR=
USER=
GROUP=
WORKERS=3
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=$DIR/.venv/bin/activate
BIND=unix:&DIR/run/gunicorn.sock
LOG_LEVEL=error

cd $DIR
source $VENV

exec gunicorn src.app.api:app \
	--name $NAME \
	--workers $WORKERS \
	--worker-class $WORKER_CLASS \
	--user=$USER \
	--group=$GROUP \
	--bind=$BIND \
	--log-level=$LOG_LEVEL \
	--log-file=-
