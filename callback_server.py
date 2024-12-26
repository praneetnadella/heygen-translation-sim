from flask import Flask, request, jsonify
import requests
from utils.logger import serverLog, serverError

# {clientId: callbackUrl}
registeredClients = {}

cbs = Flask(__name__)

@cbs.route('/register', methods=['POST'])
def register():
    serverLog("Registering client")
    data = request.json
    clientId = data.get('clientId')
    callbackUrl = data.get('callbackUrl')

    if not clientId or not callbackUrl:
        serverError("Missing clientId or callbackUrl")
        return jsonify({"result": "error", "message": "clientId and callbackUrl required"}), 400

    registeredClients[clientId] = callbackUrl
    serverLog(f"Client {clientId} registered with callback URL: {callbackUrl}")
    return jsonify({"result": "success", "message": "Client registered"}), 200

@cbs.route('/callback/<clientId>', methods=['POST'])
def callback(clientId):
    if clientId not in registeredClients:
        serverError(f"Client {clientId} not registered")
        return jsonify({"result": "error", "message": "Client not registered"}), 404

    callbackUrl = registeredClients[clientId]
    data = request.json
    serverLog(f"Forwarding callback to {callbackUrl}")

    try:
        response = requests.post(callbackUrl, json=data, timeout=5)
        response.raise_for_status()
        return jsonify({"result": "success", "message": "Callback forwarded", "responseCode": response.status_code}), 200
    except requests.RequestException as e:
        serverError(f"Error forwarding callback: {str(e)}")
        return jsonify({"result": "error", "message": str(e)}), 500

if __name__ == '__main__':
    serverLog("Starting callback server on port 5002")
    cbs.run(port=5002, debug=False, threaded=True)
