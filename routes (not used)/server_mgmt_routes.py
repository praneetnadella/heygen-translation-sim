# This is for server management routes

from flask import Blueprint, request, jsonify
from app import reset, setServerParams, get_all_completed_jobs_route, get_completed_jobs_route

mgmt_routes = Blueprint("mgmt_routes", __name__)

@mgmt_routes.route("/reset", methods=["POST"])
def reset_route():
    return reset()

@mgmt_routes.route("/reset/<job_id>", methods=["POST"])
def reset_specific_route(job_id):
    return reset(job_id)

@mgmt_routes.route("/set_params", methods=["POST"])
def set_params_route():
    delay = request.args.get("delay")
    error_rate = request.args.get("error_rate")
    return setServerParams(delay, error_rate)

