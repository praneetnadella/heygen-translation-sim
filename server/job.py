import time

class Job:
    def __init__(self, job_id, delay, error_rate, status="queued", client_id=None):
        self.job_id = job_id
        self.delay = delay
        self.error_rate = error_rate
        self.progress = 0
        self.start_time = None
        self.status = status
        self.client_id = client_id

    def start(self):
        self.start_time = time.time()
        self.status = "running"

    def update_progress(self) -> [str, str]:
        if not self.start_time:
            return "Job not started yet", "error"

        elapsed = time.time() - self.start_time
        # error status:
        if random.random() < self.error_rate:
            self.status = "error"
            return "Error occurred while processing", "error"
        # pending status:
        elif elapsed < self.delay:
            self.progress = int((elapsed / self.delay) * 100)
            return f"Job: {self.job_id} progress: {self.progress}%", "info"
        # completed status:
        else:
            self.progress = 100
            self.status = "completed"
            return f"Job {self.job_id} completed.", "info"

    def reset(self, delay=None, error_rate=None):
        self.start_time = None
        self.progress = 0
        self.delay = delay if delay is not None else self.delay
        self.error_rate = error_rate if error_rate is not None else self.error_rate
        self.status = "queued"
        self.client_id = None

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "delay": self.delay,
            "error_rate": self.error_rate,
            "progress": self.progress,
            "status": self.status,
            "client_id": self.client_id,
        }