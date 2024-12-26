# This file is for job status information routes

from flask import Blueprint, jsonify
from app import get_status

status_routes = Blueprint("status_routes", __name__)

@status_routes.route("/status", methods=["GET"])
def get_status_route():
    return get_status()

@status_routes.route("/status/<job_id>", methods=["GET"])
def get_status_specific_route(job_id):
    return get_status(job_id=job_id)

@status_routes.route("/status/client/<client_id>", methods=["GET"])
def get_status_client_route(client_id):
    return get_status(client_id=client_id)

@status_routes.route("/completed", methods=["GET"])
def get_all_completed_jobs():
    return get_all_completed_jobs_route()

@status_routes.route("/completed/<client_id>", methods=["GET"])
def get_completed_jobs(client_id):
    return get_completed_jobs_route(client_id)