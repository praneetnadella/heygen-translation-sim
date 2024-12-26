#!/bin/bash

# Function to show usage
usage() {
  echo "Usage: $0 <action> [job_id]"
  echo "Actions:"
  echo "  start                                 | Starts server"
  echo "  stop                                  | Stops server"
  echo "  reset                                 | Reset server"
  echo "  status                                | Check status of all jobs"
  echo "  get_clients                           | Get all clients"
  echo "  create_client [name]                  | Create new client (default: test)"
  echo "  create_job <client> [jobID]           | Create new job for client (default:test)"
  echo "  cancel_job <jobID>                    | Cancel job"
  echo "  get_job_status <jobID>                | Get status of job"
  echo "  get_client_status <clientID>          | Get status of client"
  echo "  get_completed                         | Get all completed jobs"
  echo "  get_client_completed <clientID>       | Get all completed jobs for client"
  echo "  test                                  | Run integration test"
  exit 1
}

JOB_ID=$2
SERVER_PORT=5001
CALLBACK_PORT=5002
CLIENT_PORT=5003
SERVER_LOG="logs/server.log"
CALLBACK_LOG="logs/callback.log"
CLIENT_LOG="logs/client.log"
SERVER_PID_FILE="utils/server.pid"
CALLBACK_PID_FILE="utils/callback.pid"
CLIENT_PID_FILE="utils/client.pid"

start_server() {
  if [ -f "$SERVER_PID_FILE" ]; then
    echo "Server already running on PID: $(cat $SERVER_PID_FILE)"
    return
  fi
  echo "Starting server on port $SERVER_PORT"
  python main.py > "$SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" > "$SERVER_PID_FILE"

  echo "Starting callback server on port $CALLBACK_PORT"
  python callback_server.py > "$CALLBACK_LOG" 2>&1 &
  CALLBACK_PID=$!
  echo "$CALLBACK_PID" > "$CALLBACK_PID_FILE"
  sleep 2
}

stop() {
  if [ -f "$SERVER_PID_FILE" ]; then
    SERVER_PID=$(cat "$SERVER_PID_FILE")
    echo "Stopping server"
    kill "$SERVER_PID" && rm "$SERVER_PID_FILE"
    echo "Server stopped."
  else
    echo "Server not running."
  fi

  if [ -f "$CALLBACK_PID_FILE" ]; then
    CALLBACK_PID=$(cat "$CALLBACK_PID_FILE")
    echo "Stopping callback server"
    kill "$CALLBACK_PID" && rm "$CALLBACK_PID_FILE"
    echo "Callback server stopped."
  else
    echo "Callback server not running."
  fi

  if [ -f "$CLIENT_PID_FILE" ]; then
    CLIENT_PID=$(cat "$CLIENT_PID_FILE")
    echo "Stopping client server"
    kill "$CLIENT_PID" && rm "$CLIENT_PID_FILE"
    echo "Client server stopped."
  else
    echo "Client server not running."
  fi
}

reset() {
  echo "Resetting entire server"
  curl -X POST "http://localhost:$SERVER_PORT/reset"
}

start_client() {
  if [ -f "$CLIENT_PID_FILE" ]; then
    echo "Client already running on PID: $(cat $CLIENT_PID_FILE)"
    return
  fi
  echo "Starting client on port $CLIENT_PORT"
  # python client.py > "$CLIENT_LOG" 2>&1 &
  python client.py 2>&1 | tee "$CLIENT_LOG" &
  CLIENT_PID=$!
  CLIENT_PID=$((CLIENT_PID - 1))   
  echo "$CLIENT_PID" > "$CLIENT_PID_FILE"
  sleep 2
}

get_clients() {
  echo "Getting all clients"
  curl "http://localhost:$CLIENT_PORT/get_clients"
}


status() {
  echo "Checking status of all jobs"
  curl "http://localhost:$SERVER_PORT/status"
}

create_client() {
  if [ -z "$1" ]; then
    echo "Creating new client with default name"
    curl -X POST "http://localhost:$CLIENT_PORT/create_client"
  else
    echo "Creating new client: $1"
    curl -X POST "http://localhost:$CLIENT_PORT/create_client/$1"
  fi
}


create_job() {
  local client_id="$1"
  local job_id="$2"

  if [ -z "$client_id" ]; then
    echo "Client ID required"
    return 1
  fi

  echo "Creating job for client: $client_id"
  if [ -z "$job_id" ]; then
    curl -X POST "http://localhost:$CLIENT_PORT/create_job/$client_id"
  else
    curl -X POST "http://localhost:$CLIENT_PORT/create_job/$client_id?jobId=$job_id"
  fi
}

cancel_job() {
  local job_id="$1"
  if [ -z "$job_id" ]; then
    echo "Job ID required"
    return 1
  fi
  echo "Cancelling job: $job_id"
  curl -X POST "http://localhost:$SERVER_PORT/cancel/$job_id"
}

get_job_status() {
  local job_id="$1"
  if [ -z "$job_id" ]; then
    echo "Job ID required"
    return 1
  fi
  echo "Getting status for job: $job_id"
  curl "http://localhost:$SERVER_PORT/status/$job_id"
}

get_client_status() {
  local client_id="$1"
  if [ -z "$client_id" ]; then
    echo "Client ID required"
    return 1
  fi
  echo "Getting status for client: $client_id"
  curl "http://localhost:$SERVER_PORT/status/client/$client_id"
}

get_completed() {
  echo "Getting all completed jobs"
  curl "http://localhost:$SERVER_PORT/completed"
}

get_client_completed() {
  local client_id="$1"
  if [ -z "$client_id" ]; then
    echo "Client ID required"
    return 1
  fi
  echo "Getting completed jobs for client: $client_id"
  curl "http://localhost:$SERVER_PORT/completed/$client_id"
}


test() {
  echo "Running integration test"
  python3 testing/integration_test.py
  
}

case $1 in
  start)
    start_server
    start_client
;;
  reset)
    reset
    ;;
  stop)
    stop
    ;;
  status)
    status
    ;;
  get_clients)
    get_clients
    ;;
  create_client)
    create_client "$2"
    ;;
  create_job)
    create_job "$2" "$3"
    ;;
  simple_test)
    start_server
    start_client
    create_client
    create_job
    create_job
    create_job
    status
    ;;
  test)
    test
    ;;
  cancel_job)
    cancel_job "$2"
    ;;
  reset_job)
    reset_job "$2"
    ;;
  get_job_status)
    get_job_status "$2"
    ;;
  get_client_status)
    get_client_status "$2"
    ;;
  get_completed)
    get_completed
    ;;
  get_client_completed)
    get_client_completed "$2"
    ;;
  *)
    usage
    ;;
esac