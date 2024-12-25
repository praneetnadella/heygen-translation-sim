from flask import Flask, jsonify, request
import time
import random
import logging
import uuid
from collections import deque
import threading
from job import Job


app = Flask(__name__)

job_queue = deque()
jobs = {}
curr_job_id = 0
lock = threading.Lock()

# mock config for sim (use this to set a global delay and error rate for easier debugging)
default_config = {
    "delay": random.randint(5, 15),
    "error_rate": 0.1,
}

testing = True

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

def log(message, type="info"):
    if type == "error":
        logging.error(f"SERVER ERROR: {message}")
    else:
        logging.info(f"SERVER LOG: {message}")

def process_next_job():
    global curr_job_id
    while True:
        with lock:
            if not curr_job_id and job_queue:
                curr_job_id = job_queue.popleft()
                job = jobs[curr_job_id]
                job.start()
                log(f"Job {curr_job_id} started")
        if curr_job_id:
            job = jobs[curr_job_id]
            msg, err_type = job.update_progress()
            log(msg, type=err_type)
            if job.status in ["completed", "error"]:
                log(f"Job {curr_job_id} {job.status}")
                with lock:
                    curr_job_id = None
        time.sleep(1)

threading.Thread(target=process_next_job, daemon=True).start()

# creates a new simulation job
@app.route("/create_job", methods=["POST"])
def create_job():
    job_id = str(uuid.uuid4())
    delay = default_config["delay"] if testing else random.randint(5, 15)
    error_rate = default_config["error_rate"] if testing else 0.1
    job = Job(job_id, delay, error_rate)
    jobs[job_id] = job
    job_queue.append(job_id)
    log(f"Created job ID: {job_id}")
    return jsonify(job.to_dict())

# gets the status of the simulation
@app.route("/status", methods=["GET"])
@app.route("/status/<job_id>", methods=["GET"])
def get_status(job_id=None):
    if job_id:
        log(f"GetStatus: Recieved a request to /status/{job_id}")
        if job_id not in jobs:
            log(f"GetStatus: Job ID {job_id} not found", type="error")
            return jsonify({"result": "error", "message": f"Job ID {job_id} not found"}), 404
        job = jobs[job_id]
        msg, err_type = job.update_progress()
        log(msg, type=err_type)
        return jsonify(job.to_dict())

    log("GetStatus: Received a request to /status")
    all_statuses = {job_id: job.to_dict() for job_id, job in jobs.items()}
    return jsonify(all_statuses)


# resets the simulation
@app.route("/reset", methods=["POST"])
@app.route("/reset/<job_id>", methods=["POST"])
def reset(job_id=None):
    global job_queue, jobs, curr_job_id, default_config
    
    with lock:

        if job_id:
            log(f"RESET: Received a request to /reset/{job_id}")
            if job_id not in jobs:
                log(f"RESET: Job {job_id} not found", level="error")
                return jsonify({"error": "Job not found"}), 404

            job = jobs[job_id]
            if curr_job_id == job_id:  # if resetting currently running job
                log(f"RESET: Stopping running job {job_id} for reset")
                curr_job_id = None

            job.reset()
            log(f"RESET: Job {job_id} reset successfully")
            return jsonify(job.to_dict())

        # Reset all jobs
        log("RESET: Received a request to /reset")

        if curr_job_id:  # stop curr running job
            log(f"RESET: Stopping running job {curr_job_id}")
            curr_job_id = None

        # Clear all jobs and reset global variables
        job_queue.clear()
        jobs.clear()

        # Config delay and error rate, defaults to random values between 5-15 and 0.1 respectively
        # example req: http://localhost:5001/reset?delay=10&error_rate=0.2
        new_delay = request.args.get("delay", None, type=int)
        new_error_rate = request.args.get("error_rate", None, type=float)

        # config["start_time"] = time.time()
        default_config = {
            "delay": new_delay if new_delay is not None else random.randint(5, 15),
            "error_rate": new_error_rate if new_error_rate is not None else 0.1,
        }
        # config["progress"] = 0

    log(f"RESET: Sim reset with delay: {default_config['delay']} seconds and error rate: {default_config['error_rate']:.2f}")
    return jsonify({
        "message": "Server reset successfully",
        "new_delay": default_config["delay"],
        "new_error_rate": default_config["error_rate"],
    })



if __name__ == "__main__":
    app.run(port=5001, debug=True) 