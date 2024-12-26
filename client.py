import requests
import time
import uuid
from utils.logger import clientLog, clientError
from flask import Flask, request, jsonify

client = Flask(__name__)

class VideoTransClient:

    def __init__(self, baseUrl, callbackUrl, clientId=None, pollingInterval=3, maxTimeout=30, autoPoll=True):
        self.baseUrl = baseUrl
        self.pollingInterval = pollingInterval
        self.maxTimeout = maxTimeout
        self.jobs = {}
        self.clientId = str(uuid.uuid4()) if not clientId else clientId
        self.autoPoll = autoPoll
        self.callbackUrl = callbackUrl

    def createJob(self, id=None):
        try:
            if id:
                response = requests.post(f"{self.baseUrl}/create_job/{self.clientId}?jobId={id}")
            else:
                response = requests.post(f"{self.baseUrl}/create_job/{self.clientId}")
            clientLog(f"Creating job for client {self.clientId}", self.clientId)
            response.raise_for_status()
            jobData = response.json()
            jobId = jobData.get("jobId")
            self.jobs[jobId] = {"status": "queued", "progress": 0}
            clientLog(f"Job created: {jobId}", clientId=self.clientId)
            return {"result": "success", "jobId": jobId}
        except requests.RequestException as err:
            clientError(f"Job creation failed: {err}", self.clientId)
            return {"result": "error", "message": str(err)}


    # get the status of sim either specific or all
    def getStatus(self, jobId=None):
        try:
            if jobId:
                if jobId not in self.jobs:
                    clientError(f"GetStatus: Job ID {jobId} not found in client records", self.clientId)
                    return {"result": "error", "message": "No job ID found"}
                response = requests.get(f"{self.baseUrl}/status/{jobId}")
            else:
                response = requests.get(f"{self.baseUrl}/status")
            response.raise_for_status()
            statusInfo = response.json()
            if jobId:
                self.jobs[jobId]["status"] = statusInfo.get("status", "error")
                self.jobs[jobId]["progress"] = statusInfo.get("progress", 0)
            clientLog(f"GetStatus: Status fetched for job {jobId}", self.clientId)
            return {"result": "success", "data": statusInfo}
        except requests.RequestException as err:
            clientError(f"GetStatus: Error during status fetch: {err}", self.clientId)
            return {"result": "error", "message": str(err)}

    # constant polling as described in basic implementation
    def waitForCompletion(self, jobId):
        if jobId not in self.jobs:
            clientError(f"WFC: Job {jobId} not found", self.clientId)
            return {"result": "error", "message": "Job not found"}
        
        startTime = time.time()
        while time.time() - startTime < self.maxTimeout:
            statusInfo = self.getStatus(jobId)
            jobStatus = statusInfo.get("status")
            self.jobs[jobId]["status"] = jobStatus
            self.jobs[jobId]["progress"] = statusInfo.get("progress", 0)
            if jobStatus == "completed":
                clientLog(f"WFC: Job {jobId} completed", self.clientId)
                return {"result": "completed", data: statusInfo}
            elif jobStatus == "error":
                clientError(f"WFC: Job {jobId} failed", self.clientId)
                return {"result": "error", "message": "Job failed", "data": statusInfo}
            clientLog(f"WFC: Job {jobId}: {jobStatus}, {statusInfo.get('progress', 0)}%", self.clientId)
            time.sleep(self.pollingInterval)

            
        clientError(f"WFC: Job {jobId} timed out", self.clientId)
        return {"result": "error", "message": "Job timed out"}

    # wait for all jobs to be done for a client
    def waitForAll(self):
        if not self.autoPoll:
            clientLog("WFA: Auto-polling off", self.clientId)
            return {"result": "error", "message": "Auto-polling off"}
        results = {}
        for jobId in list(self.jobs.keys()):
            clientLog(f"WFA: Waiting for job {jobId}", self.clientId)
            result = self.waitForCompletion(jobId)
            results[jobId] = result
            if result["result"] == "error":
                clientError(f"Job {jobId} failed", self.clientId)
        clientLog("WFA: All jobs completed", self.clientId)
        return {"result": "success", "data": results}

    # this just gets the current status of ajob instead of waiting for completion
    def pollJob(self, jobId):
        if self.autoPoll:
            clientLog("Auto-polling is on", self.clientId)
        if jobId not in self.jobs:
            clientError(f"Job {jobId} not found", self.clientId)
            return {"result": "error", "message": "Job not found"}
        statusInfo = self.getStatus(jobId)
        clientLog(f"Job {jobId}: {statusInfo.get('status')}, {statusInfo.get('progress', 0)}%", self.clientId)
        return statusInfo

    # this just gets the current status of all jobs instead of waiting for completion
    def pollAll(self):
        if self.autoPoll:
            clientLog("Auto-polling is on", self.clientId)
        clientLog("Polling all jobs", self.clientId)
        allStatuses = self.getStatus()
        if allStatuses.get("result") == "error":
            clientError("Failed to fetch job statuses", self.clientId)
            return {"result": "error", "message": "Failed to fetch job statuses"}
        for jobId, statusInfo in allStatuses.items():
            clientLog(f"Job {jobId}: {statusInfo.get('status')}, {statusInfo.get('progress', 0)}%", self.clientId)
        return allStatuses

def get_clients():
    if 'clients' not in client.config:
        client.config['clients'] = {}
    return client.config['clients']


@client.route("/create_client", methods=['POST'])
@client.route("/create_client/<name>", methods=['POST'])
def createClient(name=None, baseUrl="http://localhost:5001", callbackServerUrl="http://localhost:5002"):
    clients = get_clients()
    client = VideoTransClient(clientId=name, baseUrl=baseUrl, callbackUrl=callbackServerUrl)
    clients[client.clientId] = client
    # register client with the callback server
    try:
        response = requests.post(f"{callbackServerUrl}/register", json={"clientId": client.clientId, "callbackUrl": f"http://localhost:5003/callback/{client.clientId}"})
        response.raise_for_status()
        clientLog(f"Client {client.clientId} registered", client.clientId)
        return jsonify({"result": "success", "clientId": client.clientId})
    except requests.RequestException as err:
        clientError(f"Client registration failed: {err}", client.clientId)
        return jsonify({"result": "error", "message": str(err)})

@client.route("/get_clients", methods=['GET'])
def getClients():
    clients = get_clients()
    clientLog("Fetching clients", None)
    return jsonify({"result": "success", "data": list(clients.keys())})

@client.route("/callback/<clientId>", methods=['POST'])
def callback(clientId):
    clients = get_clients()
    if clientId not in clients:
        clientError(f"Client {clientId} not found")
        return jsonify({"result": "error", "message": "Client not found"}), 404
    client = clients[clientId]
    data = request.json
    jobId = data.get("jobId")
    status = data.get("status")
    progress = data.get("progress")
    if jobId not in client.jobs:
        clientError(f"Job {jobId} not found for client {clientId}")
        return jsonify({"result": "error", "message": "Job not found"}), 404
    client.jobs[jobId]["status"] = status
    client.jobs[jobId]["progress"] = progress
    clientLog(f"Callback received for job {jobId} with status {status}", clientId)
    print(f"Callback received for job {jobId} with status {status}")
    return jsonify({"result": "success", "message": "Callback received"})

@client.route("/create_job/<clientId>", methods=['POST'])
def createJobRoute(clientId):
    clients = get_clients()
    if clientId not in clients:
        clientError(f"Client {clientId} not found", clientId)
        return jsonify({"result": "error", "message": "Client not found"}), 404
    client = clients[clientId]
    # get job id from optional request data
    jobId = request.args.get("jobId")
    jobId = client.createJob(jobId)
    if jobId:
        return jsonify({"result": "success", "jobId": jobId})
    else:
        return jsonify({"result": "error", "message": "Failed to create job"}), 500

if __name__ == "__main__":
    # client = create_client()

    # job1 = client.create_job()
    # job2 = client.create_job()
    # job3 = client.create_job()
    # # job2 = None

    # if job1 or job2 or job3:
    #     client.wait_for_all()
    # else:
    #     client_log("Job creation failed", client.client_id)
    #     exit(1)

    # client_log("Fetching all job statuses:", client.client_id)
    # all_statuses = client.get_status()
    # client_log(all_statuses, client.client_id)
    # exit(1)

    client.run(port=5003, debug=True)

