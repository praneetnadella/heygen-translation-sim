import time
import random

class Job:
    def __init__(self, jobId, delay, errorRate, clientId, callbackUrl=None, status="queued"):
        self.jobId = jobId
        self.delay = delay
        self.errorRate = errorRate
        self.progress = 0
        self.startTime = None
        self.status = status   #initial status
        self.clientId = clientId
        self.callbackUrl = callbackUrl        # used by server to send job update on end

    def start(self):
        self.startTime = time.time()
        self.status = "running"

    def updateProgress(self):
        if not self.startTime:
            return {"result": "error", "message": "Job not started yet"}

        elapsed = time.time() - self.startTime
        # error status:
        if random.random() < self.errorRate:
            self.status = "error"
            return {"result": "error", "message": "Error occurred while processing"}
        # pending status:
        elif elapsed < self.delay:
            self.progress = int((elapsed / self.delay) * 100)
            return {"result": "success", "message": f"Job: {self.jobId} progress: {self.progress}%"}
        # completed status:
        else:
            self.progress = 100
            self.status = "completed"
            return {"result": "success", "message": f"Job {self.jobId} completed."}

    def reset(self, delay=None, errorRate=None):
        self.startTime = None
        self.progress = 0
        self.delay = delay if delay is not None else self.delay
        self.errorRate = errorRate if errorRate is not None else self.errorRate
        self.status = "queued"
    
    def getPublicStatus(self):
        if self.status in ["queued", "running"]:
            return "Pending"
        elif self.status == "completed":
            return "Completed"
        elif self.status == "error":
            return "Error"
        else:
            return "Error"  #default (in case more statuses are added)

    def toDict(self):
        return {
            "jobId": self.jobId,
            "delay": self.delay,
            "errorRate": self.errorRate,
            "progress": self.progress,
            "status": self.getPublicStatus(),
            "clientId": self.clientId,
        }