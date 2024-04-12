#!/usr/bin/env sh

RUN_CMD=${RUN_CMD:='server'}

start_server()
{
    exec 2>&1
    exec gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
}

help()
{
  echo "Please, use one of the: server"
  echo "Default command is server"
}


case "$RUN_CMD" in
    "server")
        start_server
        ;;
    "")
        echo "No command provided"
        help
        exit 1
        ;;
    *)
        echo "Unknown command --> $1"
        help
        exit 1
        ;;
esac
