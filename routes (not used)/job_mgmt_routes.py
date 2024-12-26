# This file is for job_management routes

from flask import Blueprint, request, jsonify
from app import create_job, cancel_job

job_routes = Blueprint("job_routes", __name__)

@job_routes.route("/create_job/<client_id>", methods=["POST"])
def create_job_route(client_id):
    job_id = request.args.get("job_id")  #gets name of job if set
    callback_url = request.args.get("callback_url")  # to respond to client
    return create_job(client_id, job_id, callback_url)

@job_routes.route("/cancel/<job_id>", methods=["POST"])
def cancel_job_route(job_id):
    return cancel_job(job_id)

    