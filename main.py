from flask import Flask, jsonify, request, Blueprint
import time
import random
import uuid
import requests
from queue import Queue
import threading

from job import Job
from utils.logger import serverLog, serverError

app = Flask(__name__)

# Global variables
jobQueue = Queue()
jobs = {}  # {job_id: Job...}
clientJobs = {} # {client_id: [job1, job2, ...]}
completedJobs = {} # {client_id:[completed_job1, completed_job2, ...]}
currJob_Id = 0
lock = threading.Lock()         # locking so shared resources updated safely, also for future use when multiple servers/clients

# mock config for sim (use to set global delay and error rate for easier debugging)
defaultConfig = {
    "delay": random.randint(5, 15),
    "errorRate": 0.1,
}

testing = True  # use default config for testing

# process next job in queue
def processJob():
    global currJobId
    while True:             # This is so each server processes one job at a time
        try:
            currJobId = jobQueue.get(timeout=1)  # Use thread-safe Queue
        
            with lock:
                job = jobs.get(currJobId)
                if not job:
                    serverError(f"Job ID {currJobId} not found")
                    currJobId = None
                    continue
            job.start()
            serverLog(f"Job {currJobId} started")

            pollRate = max(1, job.delay * 0.1) # Polling rate is 10% of delay

            while job.status not in ["completed", "error"]:             # Polling loop
                with lock:
                    msg, errType = job.updateProgress()
                if errType == "error":
                    serverError(msg)
                else:
                    serverLog(msg)
                time.sleep(pollRate)           # Dynamically adjust poll rate

            serverLog(f"Job {currJobId} {job.status}")
            notifyClient(job.callbackUrl, job.toDict())
            with lock:
                if job.status == "completed":
                    # Move to completed list
                    clientJobs[job.clientId].remove(job)
                    completedJobs.setdefault(job.clientId, []).append(job)
                elif job.status == "error":
                    # Reset job and put back in queue
                    job.reset()
                    jobQueue.put(currJobId)

            currJobId = None
        except:
            continue

# lessens polling burden by returning response to client on complete/error
def notifyClient(callbackUrl, jobData, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(callbackUrl, json=jobData)
            response.raise_for_status()
            serverLog(f"Update sent to: {callbackUrl}, Response: {response.status_code}")
            return True
        except Exception as e:
            serverError(f"Failed to notify client (attempt {attempt + 1}) at callback {callbackUrl}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponentially backoff
    serverError(f"Notification to client failed after {retries} retries")
    return False

threading.Thread(target=processJob, daemon=True).start()       # Start processing jobs (allows for processing while accepting other requests)

# creates a new simulation job
def createJob(clientId=None, jobId=None, callbackUrl=None):
    if not clientId:
        serverError("Client ID required")
        return jsonify({"error": "Client ID required"}), 400

    if not jobId:
        jobId = str(uuid.uuid4())      # Generate random ID
    elif jobId in jobs:  # prevent dup ids
        serverError(f"Job ID {jobId} already exists")
        return jsonify({"error": f"Job ID {jobId} already exists"}), 400

    delay = defaultConfig["delay"] if testing else random.randint(5, 15)
    errorRate = defaultConfig["errorRate"] if testing else 0.1
    job = Job(jobId, delay, errorRate, clientId, callbackUrl)   # Create job object

    # update data structures
    jobs[jobId] = job
    jobQueue.put(jobId)
    clientJobs.setdefault(clientId, []).append(job)  

    serverLog(f"Created job ID: {jobId} for client ID: {clientId}")
    return jsonify(job.toDict())

# cancel a job
def cancelJob(jobId):
    with lock:
        job = jobs.get(jobId)
        if not job or job.status in ["completed", "error"]:
            serverError(f"Cannot cancel job {jobId} since status is {job.status}")
            return jsonify({"error": "Cannot cancel job"}), 400
        job.status = "cancelled"
        #move job to completed list
        clientJobs[job.clientId].remove(job)
        completedJobs.setdefault(job.clientId, []).append(job)
        return jsonify({"message": "Job cancelled successfully"})

# Gts the status of all incomplete jobs or a specific incomplete job
def getStatus(jobId=None, clientId=None):
    # to output a specific job
    if jobId:
        serverLog(f"GetStatus: Received a request to /status/{jobId}")
        if jobId not in jobs:
            serverError(f"GetStatus: Job ID {jobId} not found")
            return jsonify({"status": "error", "message": f"Job ID {jobId} not found"}), 404
        return jsonify(jobs[jobId].toDict())
    
    # To output all jobs of a client
    if clientId:
        serverLog(f"GetStatus: Received a request for all jobs of client {clientId}")
        if clientId not in clientJobs:
            return jsonify({"status": "error", "message": f"No jobs found for client {clientId}"}), 404
        return jsonify([job.toDict() for job in clientJobs[clientId]])

    serverLog("GetStatus: Received a request to /status")
    return jsonify({jobId: job.toDict() for jobId, job in jobs.items()})

# resets either the entire server or a specific job
def reset(jobId=None):
    global jobQueue, jobs, currJobId, defaultConfig
    with lock:
        if jobId:
            serverLog(f"RESET: Received a request to /reset/{jobId}")
            job = jobs.pop(jobId, None)
            if not job:
                serverError(f"RESET: Job {jobId} not found")
                return jsonify({"error": "Job not found"}), 404
            if currJobId == jobId:  # if resetting currently running job
                serverLog(f"RESET: Stopping running job {jobId} for reset")
                currJobId = None
            
            job.reset()
            jobQueue.put(jobId)  # push back to back of queue
            serverLog(f"RESET: Job {jobId} reset successfully")
            return jsonify(job.toDict())

        # Reset all jobs
        serverLog("RESET: Received a request to /reset")
        currJobId = None # stop curr running job

        # Clear all jobs and reset global variables
        while not jobQueue.empty():
            jobQueue.get()
        jobs.clear()
        clientJobs.clear()
    return jsonify({"message": "Server reset successfully",})

# sets the server parameters for delay and error rate
def setServerParams(delay, errorRate):
    try:
        delay = int(delay)
        errorRate = float(errorRate)
        if delay <= 0 or not (0 <= errorRate <= 1):
            raise ValueError("Invalid delay or errorRate values")

        defaultConfig["delay"] = delay
        defaultConfig["errorRate"] = errorRate
        serverLog(f"Server parameters updated: delay={delay}, errorRate={errorRate}")
        return jsonify({"message": "Server parameters updated successfully", "delay": delay, "errorRate": errorRate})
    except ValueError as e:
        serverError(f"Invalid parameters: {e}")
        return jsonify({"error": "Invalid parameters", "details": str(e)}), 400

# -------------------------------------- Routes -------------------------------------- #

# routes that require locks and global vars
def getAllCompletedJobsRoute():
    with lock:
        completed = completedJobs  # so lock can release and continue, just grabs a snapshot of curr dict
    return jsonify([job.toDict() for client in completed for job in completed[client]])

def getCompletedJobsRoute(clientId):
    serverLog(f"Get completed jobs for client {clientId}")
    if clientId not in clientJobs:
        return jsonify({"error": f"Client {clientId} not found"}), 404
    with lock:
        completed = completedJobs.get(clientId, [])
    return jsonify([job.toDict() for job in completed])

'''Changed to Blueprints originally to move functions to separate files
    but decided to keep them in the same file to keep it working for now'''
jobRoutes = Blueprint("jobRoutes", __name__)  

@jobRoutes.route("/create_job/<clientId>", methods=["POST"])
def createJobRoute(clientId):
    serverLog(f"Received request to create job for client {clientId}")
    callbackUrl = f"http://localhost:5002/callback/{clientId}"
    jobId = request.args.get("jobId", None)  #gets name of job if set
    return createJob(clientId, jobId, callbackUrl)

@jobRoutes.route("/cancel/<jobId>", methods=["POST"])
def cancelJobRoute(jobId):
    return cancelJob(jobId)

mgmtRoutes = Blueprint("mgmtRoutes", __name__)

@mgmtRoutes.route("/reset", methods=["POST"])
def resetRoute():
    return reset()

@mgmtRoutes.route("/reset/<jobId>", methods=["POST"])
def resetSpecificRoute(jobId):
    return reset(jobId)

@mgmtRoutes.route("/set_params", methods=["POST"])
def setParamsRoute():
    delay = request.args.get("delay")
    errorRate = request.args.get("errorRate")
    return setServerParams(delay, errorRate)

statusRoutes = Blueprint("statusRoutes", __name__)

@statusRoutes.route("/status", methods=["GET"])
def getStatusRoute():
    return getStatus()

@statusRoutes.route("/status/<jobId>", methods=["GET"])
def getStatusSpecificRoute(jobId):
    return getStatus(jobId=jobId)

@statusRoutes.route("/status/client/<clientId>", methods=["GET"])
def getStatusClientRoute(clientId):
    return getStatus(clientId=clientId)

@statusRoutes.route("/completed", methods=["GET"])
def getAllCompletedJobs():
    return getAllCompletedJobsRoute()

@statusRoutes.route("/completed/<clientId>", methods=["GET"])
def getCompletedJobs(clientId):
    return getCompletedJobsRoute(clientId)

# Bluprints for request routing
app.register_blueprint(jobRoutes)
app.register_blueprint(statusRoutes)
app.register_blueprint(mgmtRoutes)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
