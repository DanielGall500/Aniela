#!/bin/bash
NAME=translate-api
USER=dg
GROUP=dg
WORKERS=4 
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=$DIR/venv/bin/activate
BIND=unix:$DIR/run/gunicorn.sock
LOG_LEVEL=error

gunicorn app.api:app \
	--name $NAME \
	--preload \
	--workers $WORKERS \
	--worker-class $WORKER_CLASS \
	--bind "0.0.0.0:80" \
	--timeout 120 \
	--keep-alive 200
