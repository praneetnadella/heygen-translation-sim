import requests
import time

BASE_URL = "http://localhost:5003"

def create_client():
    response = requests.post(f"{BASE_URL}/create_client/test_client")
    print(f"Create client response: {response.json()}")
    return response.json().get("clientId")

def create_job(client_id):
    response = requests.post(f"{BASE_URL}/create_job/{client_id}")
    print(f"Create job response: {response.json()}")
    return response.json().get("jobId")

def run_test():
    print("----------------------------------------------------")
    print("Starting integration test...")
    print("----------------------------------------------------")
    client_id = create_client()
    
    if not client_id:
        print("Failed to create client")
        return
    
    for i in range(3):
        job_id = create_job(client_id)
        if not job_id:
            print(f"Failed to create job {i+1}")
        else:
            print(f"Created job {i+1} with ID: {job_id}")
    
    print("Integration test completed")
    print("----------------------------------------------------")


if __name__ == "__main__":
    run_test()
