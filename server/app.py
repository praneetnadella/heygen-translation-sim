from flask import Flask, jsonify
import time
import random

app = Flask(__name__)

# mock config for sim
config = {
    "start_time": time.time(),
    "delay": random.randint(5, 15),
    "error_rate": 0.1,
    "progress": 0
}

# gets the status of the simulation
@app.route("/status", methods=["GET"])
def get_status():
    # error status:
    if random.random() < config["error_rate"]:
        return jsonify({"result": "error"})

    elapsed = time.time() - config["start_time"]

    # pending status:
    if elapsed < config["delay"]:
        config["progress"] = int((elapsed / config["delay"]) * 100)
        return jsonify({"result": "pending", "progress": config["progress"]})

    # completed status:
    return jsonify({"result": "completed"})

# resets the simulation
@app.route("/reset", methods=["POST"])
def reset_simulation():
    config["start_time"] = time.time()
    config["delay"] = random.randint(5, 15)
    config["progress"] = 0
    return jsonify({"message": "Reset the sim", "delay": config["delay"]})

if __name__ == "__main__":
    app.run(port=5001, debug=True) 