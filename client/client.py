import requests
import time

class VideoTransClient:

    # basic init with params
    def __init__(self, base_url, polling_interval=2, max_timeout=30):
        self.base_url = base_url
        self.polling_interval = polling_interval
        self.max_timeout = max_timeout

    # get the status of sim
    def get_status(self):
        try:
            response = requests.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            print(f"Error while fetching status: {err}")
            return {"result": "error", "message": str(err)}

    # constant polling as described in basic implementation
    def wait_for_completion(self):
        start_time = time.time()

        while time.time() - start_time < self.max_timeout:
            status_info = self.get_status()
            job_status = status_info.get("result")

            print(f"Job status: {job_status}")
            if "progress" in status_info:
                print(f"Progress: {status_info['progress']}%")

            if job_status == "completed":
                print("Job completed.")
                return "completed"
            elif job_status == "error":
                print("Job failed.")
                return "error"

            time.sleep(self.polling_interval)

        print("Timeout: too long to complete")
        return "timeout"


if __name__ == "__main__":
    client = VideoTransClient(base_url="http://localhost:5001")
    final_result = client.wait_for_completion()
    print(f"Final Result (main): {final_result}")