# Heygen Translation Simulation

This project simulates a video translation server and provides a client library for interacting with the server. The goal is to create an efficient mechanism for querying the status of a video translation process while minimizing cost and delays.

## Problem Description

HeyGen video translation process can be time-consuming, depending on the video's length and other factors. Please:

1. Write a **server** to simulate the backend for video translation.
2. Implement a **client library** to interact with this server efficiently.

---

## Server Implementation

The server provides a `GET /status` API that returns the current status of a video translation process. The status can be one of the following:

- **Pending**: The translation is still in progress.
- **Completed**: The translation has finished successfully.
- **Error**: An error occurred during the process.

### Key Features

- **Random Delay Simulation**: Configurable delay to simulate processing time.
- Returns **Pending** until the configured time has passed.

---

## Client Library

The client library is designed to interact with the server's `GET /status` endpoint. It aims to improve over a trivial implementation by:

- Avoiding frequent calls to reduce unnecessary costs.
- Minimizing delays in fetching the status.
- Wrapping errors for better usability.

### Trivial Approach vs Improved Approach

| Feature                 | Trivial Implementation         | Improved Implementation         |
|-------------------------|--------------------------------|---------------------------------|
| **API Calls** | Simple HTTP calls              | Optimized for efficiency        |
| **Error Handling** | Basic                          | Comprehensive error wrapping    |
| **Polling** | User-driven, frequent polling  | Intelligent, adaptive polling   |

---

## Deliverables

### 1. Public GitHub Repository

### 2. Integration Test

A test script that:
- Spins up the server.
- Demonstrates the usage of the client library.
- Print logs showing the status updates and polling mechanism.

### 3. Documentation

Modules Imported:
- `flask`
- `random`
- `time`
- `requests`
- `uuid`
- `json`
- `threading`

For those missing, please run `pip3 install -r {module}`

Default settings:
- Autopoll On: Client polls for status updates automatically.
- Delay: A random number between 5 and 15 seconds.
- Error Rate: 10%.
- Client ID: Randomly generated.
- Job ID: Randomly generated.

Instructions for using the client library.

For setup please:
- Clone the repository
- cd into the main directory
- Create a virtual environment and install the modules above

To further interact with the server in default mode, here are some more functions through the shell script:
- `./run.sh start` - Starts the main server, callback server, and client
- `./run.sh stop` - Stops all the servers
- `./run.sh status` - Shows the status of the server
- `./run.sh reset` - Resets the server
- `./run.sh create_client [name]` - Creates a new client with a given optional name (defaults to test)
- `./run.sh create_job <name> [jobID]` - Creates a new job for the given client with optional jobID (defaults to random)
- `./run.sh get_clients` - Gets all the clients
- `./run.sh get_completed` - Gets all the completed jobs
- `./run.sh get_client_completed <client>` - Gets all the completed jobs for a specific client by clientID
- `./run.sh get_client_status <client>` - Gets the status of the preset client by clientID
- `./run.sh get_job_status <jobID>` - Gets the status of a specific job by jobID
- `./run.sh cancel_job <jobID>` - Cancels a specific job by jobID
- `./run.sh test` - Runs the integration test

The logs for this can be seen in the logs/server.log (which shows the progress more clearly) and logs/client.log (which shows the calls) files.
Note: The logs are dense

Start by running `./run.sh start` and then `./run.sh test` to see the client library in action.

Then, feel free to use the commands to create clients, and jobs, and check the status of the jobs and clients.

Note: the terminal may not show it is able to take input but it can.

Once done, please run `./run.sh stop` to stop the servers. (You may ensure stoppage by running lsof -i:xxxx where xxxx is the port number)

### Functionalities Added
- **Logging** - Added logging to the server and client to track the status of the translation process.
- **Configurable Delay and Error Rate** - Added configuration options to control the delay and error rate of the translation process (to simulate the server better)
- **Multiple Jobs Support** - Added support for multiple translation jobs on the server.
- **Client Library Improvements** - Improved the client library to account for multiple clients per server and multiple jobs per client. The client can also get the status of specific jobs, cancel jobs, and reset a job.
- **Polling Mechanism** - Implemented an adaptive polling mechanism to reduce unnecessary calls to the server. I have the option to either autoPoll by default or manually poll for the status of the job.
- **Error Handling** - Improved error handling in the client library to provide more detailed error messages.
- **Server Side** - Added functionality for dynamic polling on the server side as well, where errored jobs are moved back to the end of the queue (essentially retrying errors). Additionally, with threads, the server can process while handling requests.
- **Client Callback Server** - Added a callback server to the client library to handle callbacks from the server. This allows for more efficient polling and handling of the jobs.


### Future Improvements
- **Retry Mechanism** - Implement a better retry mechanism in the client library to handle small errors. Right now, I just move errored tasks to the end of the queue. This could be improved by having a retry mechanism that retries the job a certain number of times before giving up.
- **Client Callback Server** - Instead of one callback server which I implemented due to the smaller scale of the project on a single computer, I could have a callback server for each client. This would allow for more efficient polling, and would also allow for more efficient handling of the jobs. Additionally, this would allow for the server to be more scalable, and for the server to be more reliable. It is also more realistic that a client is calling from its own server. This would also open the door for each client to handle callbacks differently (on error: retry or cancel, on success: notify, etc.)
- **Web Interface** - Have a web interface to show more detailed information about the jobs, and to allow for more interaction with the server. This makes it easier to visualize the status of the jobs and the server for clients. For example, displaying the jobs in the queue and their status by color, when they were requested, estimated time to start/complete and a list of completed jobs. Having a client-specific page would be useful, as then the poll rate could be increased for that client when viewing the page and decreased when not.
- **Multiple Server Support** - Add support for multiple servers in the client library. This would also include the addition of a rate limiter.
- **Priority Queue** - Implement a priority queue for translation jobs in the server. This could also be supplemented by taking into account video length/difficulty and having a specific server for handling the easier tasks as well. Would also have to consider handling stalling jobs, implementing a timeout, priority donation, and updating the visual and client appropriately.
- **Estimated Time Remaining** - Add a way to get the estimated time remaining for a job to start/complete. This would be more straightforward when actual timings are added to the videos and en estimated time for each job is calculated. The implementation right now is just ... 
- **Concurrency** - Right now, I decided to make it so a server is using all its resources to translate a video. However, depending on the server, and project parameters, it might be better/asked of us to have multiple jobs running at once. This would require a more complex server/client interaction, and would also require a more complex polling mechanism. But it could lead to huge gains in the efficiency of the server. Especially if tied with the "speed server" idea, where the speed server has many threads to crank out "low impact" jobs quickly.
- **Thread Safety** - The server is not completely thread-safe right now, and could be improved to be so, especially if a thread goes down. This would allow for multiple clients to interact with the server at once, and would also allow for the server to handle multiple jobs at once.
- **Better Logging** - The logging is a bit dense right now, and could be improved to be more readable, and more informative, along with levels of logging, where each level goes more in-depth. Request IDs and timestamps could also be added.
- **Improve the AutoPolling** - The autoPolling is a bit basic right now and could be improved to be more efficient, and more accurate. This could be done by adding a "time to next poll" to the client, and having the client poll at that time, instead of polling every x seconds. Additionally, with more data, we could more accurately predict when the job will be done, and poll more efficiently. Additionally,  we can slowly phase out the auto polling of a job over time, as the job gets older, and then refresh the polling amount if that job is specifically asked for, by the client.
- **Persistence** - Right now, the server is not persistent, and if it goes down, all the jobs are lost. This could be improved by adding a database to the server and saving the jobs to the database. This would also allow for the server to be restarted, and the jobs to be picked up where they left off. Additionally, this would allow for the server to be scaled horizontally, and for multiple servers to be used at once.
- **Security** - The server is not secure right now, and could be improved by adding a token to the client, and having the server check the token before allowing the client to interact with the server. Any client can also read another client's task information if they know the job_id. I tried to start the process by attaching client_id to the job but this is not enough.
- **Testing** - The testing is not very robust right now, and could be improved by adding more tests, and more complex tests. This would also allow for the server to be more robust, and for the server to be more reliable. Additionally, this would allow for the server to be more efficient, and for the server to be more scalable.
- **Organization** - The organization of the code could be improved, and could be more modular. I began the steps to do this, but it could be improved by adding more classes and functions for repetitive code and organizing code and files by their function. This would improve scalability and also debugging due to the separation.
- **Durability** - If the callback server goes down, the client will not be able to poll for updates. This is a critical point of failure and could be improved by having the client be able to poll the server directly. This would also allow for the server to be more reliable, and for the server to be more scalable. Additionally, this would allow for the server to be more efficient, and for the server to be more robust. However having the callback server can reduce the load a little on the main server if more updates are sent to the callback server which the client can poll instead.



Notes: You may notice that a lot of this is more backend functionality rather than user-facing. As I worked on this project, I got sucked in on building out the backend, but for good reason. My thought was to represent a client accurately polling for a request by having the server account for different parameters of video translation (delay, error rate, etc.) and then build out support for new routes and identifiers. The customer might not see all these changes, but such changes must permeate across so that the user feels no hindrance in functionality. That said, I was building a stable foundation for the front end and making the server more accurately simulate the translation process. This allows me to implement optimizations beneficial to the user, such as exponential backoff, auto polling, multi-threading, and eventually, priority queueing, where the benefits now filter through to the user. I was also setting up for scaling (multiple servers, jobs, and clients). Adding endpoints to check on specific tasks and dynamically polling, along with responding when done, lowers the server strain while ensuring users get the most updated information on their translation. Additionally, introducing a web client reduces the need for a user to inquire constantly about a job. This introduces two more possibilities: removing auto polling (the website now handles this for all jobs) and faster polling on specific jobs that the client might want specific updates on. This would lower the overall burden but allow for faster updates to the user.