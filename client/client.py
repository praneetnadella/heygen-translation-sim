import requests
import time
import random

class VideoTransClient:

    # basic init with params
    def __init__(self, base_url, polling_interval=2, max_timeout=30):
        self.base_url = base_url
        self.polling_interval = polling_interval
        self.max_timeout = max_timeout
        self.jobs = {}
    
    def create_job(self):
        try:
            response = requests.post(f"{self.base_url}/create_job")
            response.raise_for_status()
            job_data = response.json()
            job_id = job_data.get("job_id")
            self.jobs[job_id] = {"status": "queued", "progress": 0}
            log(f"Created job ID: {job_id}")
            return job_id
        except requests.RequestException as err:
            log(f"Error while creating job: {err}", error=True)
            return None

    # get the status of sim either specific or all
    def get_status(self, job_id=None):
        if job_id:
            if job_id not in self.jobs:
                log(f"GetStatus: Job ID {job_id} not found in client records.", error=True)
                return {"result": "error", "message": "No job ID found"}
            try:
                response = requests.get(f"{self.base_url}/status/{job_id}")
                response.raise_for_status()
                status_info = response.json()
                self.jobs[job_id]["status"] = status_info.get("result")
                self.jobs[job_id]["progress"] = status_info.get("progress", 0)
                return status_info
            except requests.RequestException as err:
                log(f"GetStatus: Error while fetching status for job {job_id}: {err}", error=True)
                return {"result": "error", "message": str(err)}
        try:
            response = requests.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            log(f"GetStatus: Error while fetching all job statuses: {err}", error=True)
            return {"result": "error", "message": str(err)}

    # constant polling as described in basic implementation
    def wait_for_completion(self, job_id=None):
        if job_id and job_id not in self.jobs:
            log(f"WFC: Job ID {job_id} not found in client", error=True)
            return "error"
        
        start_time = time.time()
        none_count  = 0

        while time.time() - start_time < self.max_timeout:
            status_info = self.get_status(job_id)
            job_status = status_info.get("result")

            # if job_status is None:
            #     none_count += 1
            #     if none_count > 3:
            #         log(f"WFC: Job {job_id} status remains 'None' for too long. Aborting.", error=True)
            #         return "error"

            log(f"Job status: {job_status}")
            if job_status == "completed":
                log(f"WFC: Job {job_id} completed")
                return "completed"
            elif job_status == "error":
                log(f"WFC: Job {job_id} failed", error=True)
                return "error"

            log(f"WFC: Job {job_id} status: {job_status}, progress: {status_info.get('progress', 0)}%")
            time.sleep(self.polling_interval)

        log(f"WFC: Job {job_id} timed out", error=True)
        return "timeout"

    # wait for all jobs to be done
    def wait_for_all(self):
        for job_id in list(self.jobs.keys()):
            log(f"WFA: Waiting for job {job_id} to complete.")
            result = self.wait_for_completion(job_id)
            if result == "error":
                log(f"WFA: Job {job_id} failed. Continuing with remaining jobs.", error=True)





def log(message, error=False):
    if error:
        print(f"CLIENT ERROR: {message}")
    else:
        print(f"CLIENT LOG: {message}")



if __name__ == "__main__":
    client = VideoTransClient(base_url="http://localhost:5001")

    job1 = client.create_job()
    # job2 = client.create_job()
    job2 = None

    if job1 or job2:
        client.wait_for_all()
    else:
        log("Job creation failed", error=True)
        exit(1)

    log("Fetching all job statuses:")
    all_statuses = client.get_status()
    log(all_statuses)
    exit(1)


