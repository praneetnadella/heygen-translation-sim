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
| **API Calls**           | Simple HTTP calls              | Optimized for efficiency        |
| **Error Handling**      | Basic                          | Comprehensive error wrapping    |
| **Polling**             | User-driven, frequent polling  | Intelligent, adaptive polling   |

---

## Deliverables

### 1. Public GitHub Repository

### 2. Integration Test

A test script that:
- Spins up the server.
- Demonstrates the usage of the client library.
- Prints logs showing the status updates and polling mechanism.

### 3. Documentation

Instructions for using the client library.