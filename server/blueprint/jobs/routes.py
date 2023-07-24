from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ...model import db
from . import schema
from ...services import jobs as jobsService
from . import validator

jobs = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs.route("/", methods=["POST"])
def create_job():
    data = request.get_json()  # Parse the request body as JSON
    try:
        job = schema.Job(**data)  # Validate and convert the JSON data to the Job model
    except ValueError as e:
        response_data = {
            "apiVersion": "1.0",
            "context": "/jobs/",
            "error": {
                "code": 400,
                "message": "Bad Request",
                "errors": [{"message": str(e)}],
            },
        }
        return jsonify(response_data), 400

    database = db.SessionLocal()  # Create a new database session
    try:
        created_job = jobsService.create_job(
            job, database
        )  # Pass the Job model to the create_job function
        database.commit()  # Commit the changes to the database

        # Serialize the created_job data using DisplayJob model
        response_data = {
            "apiVersion": "1.0",
            "context": "/jobs",
            "data": jobsService.display_job(created_job),
        }
        return jsonify(response_data), 201
    except Exception as e:
        database.rollback()  # Rollback changes if an error occurs
        response_data = {
            "apiVersion": "1.0",
            "context": "/jobs/",
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "details": "An unexpected error occurred while processing your request. Please try again later.",
            },
        }
        return jsonify(response_data), 500, e
    finally:
        database.close()  # Always close the session after use


@jobs.route("/<jobId>", methods=["GET"])
def get_job_with_candidates(jobId):
    database = db.SessionLocal()  # Create a new database session
    try:
        job = jobsService.get_job_by_id(
            database, jobId
        )  # Use the get_job_by_id function from the jobs service
        if not job:
            # Return a 404 Not Found response if the job with the given ID doesn't exist
            response_data = {
                "apiVersion": "1.0",
                "context": f"/jobs/{jobId}",
                "error": {
                    "code": 404,
                    "message": "Not Found",
                    "errors": [{"message": "Job not found"}],
                },
            }
            return jsonify(response_data), 404

        # Assuming you have a method in the Job model to fetch candidates related to the job
        candidates = job.get_candidates(database)

        # Serialize the job and candidates data
        response_data = {
            "apiVersion": "1.0",
            "context": f"/jobs/{jobId}",
            "data": job.serialize(),
            "candidates": [candidate.serialize() for candidate in candidates],
        }
        return jsonify(response_data), 200
    finally:
        database.close()  # Always close the session after use


@jobs.route("", methods=["GET"])
def get_all_jobs():
    database = db.SessionLocal()  # Create a new database session
    try:
        all_jobs = jobsService.get_all_job(
            database
        )  # Use the get_all_job function from the jobs service
        serialized_jobs = [
            job.serialize() for job in all_jobs
        ]  # Assuming you have a serialize() method in the Job model
        return jsonify({"status": True, "data": serialized_jobs})
    finally:
        database.close()  # Always close the session after use
