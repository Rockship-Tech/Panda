from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from system import model_base
from system import schema_validator
from system.responses import Responses, SuccessResponse, ErrorResponse
from services.jobs import Jobs as jobsService
import logging
import uuid


jobs = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs.route("/", methods=["POST"])
def create_job():
    data = request.get_json()  # Parse the request body as JSON
    try:
        job = schema_validator.Job(
            **data
        )  # Validate and convert the JSON data to the Job model
    except ValueError as e:
        return ErrorResponse(context="/jobs/").bad_request_response(str(e))

    try:
        with model_base.get_db() as database:
            created_job = jobsService(database).create_job(job)

            # Serialize the created_job data using DisplayJob model
            return SuccessResponse(context="/jobs/").generate_response(
                created_job.display(), 201
            )

    except Exception as e:
        print(e)
        return ErrorResponse(context="/jobs/").internal_server_error_response()


@jobs.route("/<jobId>", methods=["GET"])
def get_job_with_candidates(jobId):
    try:
        with model_base.get_db() as db:
            job = jobsService(db).get_job_with_candidates(uuid.UUID(jobId))
            if not job:
                return ErrorResponse(context="/jobs/").not_found_response()
            else:
                return SuccessResponse(context="/jobs/").generate_response(
                    job.display(with_candidates=True), 200
                )
    except Exception as e:
        print(e)
        return ErrorResponse(context="/jobs/").internal_server_error_response()


@jobs.route("/<jobId>", methods=["DELETE"])
def delete_job_by_id(jobId):
    pass


@jobs.route("/<jobId>", methods=["PUT"])
def update_job(jobId):
    try:
        # Retrieve the job data from the request
        request_data = request.json
        # Validate the request data (you may implement validation logic here)

        with model_base.get_db() as db:
            jobs_service = jobsService(db)
            job = jobs_service.get_job_by_id(uuid.UUID(jobId))
            if not job:
                return ErrorResponse(context="/jobs/").not_found_response()
            # Update the job attributes with the new data from the request
            updated_job = jobs_service.update_job(uuid.UUID(jobId), request_data)
            if not updated_job:
                return ErrorResponse(context="/jobs/").internal_server_error_response()

            # Return a success response with the updated job data
            return SuccessResponse(context="/jobs/").generate_response(
                updated_job.display(), 200
            )

    except Exception as e:
        print(e)
        return ErrorResponse(context="/jobs/").internal_server_error_response()


@jobs.route("/", methods=["GET"])
def get_all_jobs():
    # Parse query parameters
    query_params = schema_validator.parse_query_params(request.args)
    # Validate query parameters
    validation_error = schema_validator.valid_params(query_params)
    if validation_error:
        return ErrorResponse(context="/jobs/").bad_request_response(validation_error)

    try:
        with model_base.get_db() as database:
            jobs_service = jobsService(database)
            jobs, total_jobs = jobs_service.get_all_jobs(query_params)
            logging.info(f"Total jobs: {total_jobs}")
            response_data = {
                "kind": "jobListing",
                "fields": "id,title,description,responsibilities,qualifications,work_mode,createdAt,updatedAt",
                "items": [job.display() for job in jobs],
                "page": int(query_params.get("page", 1)),
                "perPage": int(query_params.get("per_page", 10)),
                "total": total_jobs,
            }

            return SuccessResponse(context="/jobs/").generate_response(response_data)

    except Exception as e:
        # Handle the exception here, you can log the error or provide an error response
        print(e)
        return ErrorResponse(context="/jobs/").internal_server_error_response()
