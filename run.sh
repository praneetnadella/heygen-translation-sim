#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <action> [job_id]"
  echo "Actions:"
  echo "  start       Starts server"
  echo "  reset       Reset server or job w/ job_id"
  echo "  create      Create new job"
  echo "  status      Check status of all jobs or one job w/ job_id"
  exit 1
fi

JOB_ID=$2
SERVER_PORT=5001
SERVER_LOG="server.log"

start_server() {
  echo "Starting the server on port $SERVER_PORT..."
  python server/app.py > "$SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  echo "Server started with PID $SERVER_PID (logging to $SERVER_LOG)"
  sleep 2
}

reset() {
  if [ -z "$JOB_ID" ]; then     # for entire server
    echo "Resetting the entire server..."
    curl -X POST "http://localhost:$SERVER_PORT/reset"
  else
    echo "Resetting job $JOB_ID..."     # for specific job
    curl -X POST "http://localhost:$SERVER_PORT/reset/$JOB_ID"
  fi
}

start_client() {
  echo "Starting client..."
  python client/client.py &
  CLIENT_PID=$!
  echo "Client started with PID $CLIENT_PID"
}

create() {
  echo "Creating new job..."
  curl -X POST "http://localhost:$SERVER_PORT/create_job"
}
#  l
status() {
  if [ -z "$JOB_ID" ]; then         # for all jobs
    echo "Checking the status of all jobs..."
    curl "http://localhost:$SERVER_PORT/status"
  else                          # for specific job
    echo "Checking the status of job $JOB_ID..."
    curl "http://localhost:$SERVER_PORT/status/$JOB_ID"
  fi
}

case $1 in
  start)
    start_server
    start_client
;;
  reset)
    reset
    ;;
  create)
    create
    ;;
  status)
    status
    ;;
  *)
    echo "Not an action: '$ACTION'"
    exit 1
    ;;
esac