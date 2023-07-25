from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..system import model_base
from ..system import schema_validator
from ..system.responses import Responses
from ..services import jobs as jobsService
import logging

jobs = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs.route("/", methods=["POST"])
def create_job():
    data = request.get_json()  # Parse the request body as JSON
    try:
        job = schema_validator.Job(
            **data
        )  # Validate and convert the JSON data to the Job model
    except ValueError as e:
        return Responses.bad_request_response(str(e), context="/jobs/")

    database = model_base.SessionLocal()  # Create a new database session
    try:
        created_job = jobsService.create_job(
            job, database
        )  # Pass the Job model to the create_job function from the jobs service

        database.commit()  # Commit the changes to the database

        # Serialize the created_job data using DisplayJob model
        return Responses.success_response(created_job.display(), 201, context="/jobs/")

    except Exception as e:
        database.rollback()  # Rollback changes if an error occurs
        logging.error(e)
        return Responses.internal_server_error_response(context="/jobs/")

    finally:
        database.close()  # Always close the session after use


@jobs.route("/<jobId>", methods=["GET"])
def get_job_with_candidates(jobId):
    database = model_base.SessionLocal()  # Create a new database session
    try:
        job = jobsService.get_job_by_id(
            database, jobId
        )  # Use the get_job_by_id function from the jobs service
        if not job:
            return Responses.not_found_response(context=f"/jobs/{jobId}")

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
    database = model_base.SessionLocal()  # Create a new database session
    try:
        respond = Responses(context="/jobs/")
        # Parse query parameters
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        search_query = request.args.get("search", "")
        sort_by = request.args.get("sort_by", "")

        try:
            all_jobs = jobsService.get_all_job(database)
            # Filter jobs based on search query
            if search_query:
                all_jobs = [
                    job for job in all_jobs if search_query.lower() in job.title.lower()
                ]
            print(all_jobs)
            # Sort jobs based on sort_by (if provided)
            if sort_by:
                reverse = False
                if sort_by.startswith("-"):
                    sort_by = sort_by[1:]
                    reverse = True
                all_jobs.sort(key=lambda job: getattr(job, sort_by), reverse=reverse)

            # Paginate the results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_jobs = all_jobs[start_idx:end_idx]

            serialized_jobs = [
                job.display() for job in paginated_jobs
            ]  # Assuming you have a serialize() method in the Job model
            response_data = {
                "kind": "jobListing",
                "fields": "id,title,description,responsibilities,qualifications,work_mode,createdAt,updatedAt",
                "id": 1,
                "lang": "en-US",
                "updated": "2023-07-19T12:34:56Z",
                "currentItemCount": len(serialized_jobs),
                "itemsPerPage": per_page,
                "startIndex": start_idx,
                "totalItems": len(all_jobs),
                "pageIndex": page - 1,
                "totalPages": (len(all_jobs) // per_page) + 1,
                "items": serialized_jobs,
            }
            return respond.success_response(response_data, 200)

        except Exception as e:
            logging.error(e)
            return respond.internal_server_error_response()

    finally:
        database.close()  # Always close the session after use


# @jobs.route("/<jobId>", methods=["DELETE"])
# def delete_job_by_id(jobId):
