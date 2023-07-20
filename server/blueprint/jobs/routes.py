from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ...model import db
from . import schema
from . import services
from . import validator

jobs = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs.route("/create", methods=['POST'])
def create_job(request: schema.Job, database: Session = db.get_db): 
    data = request
    services.create_job(data, database)
    return jsonify({
        'status': True
    })
    
@jobs.route("/alljobs", methods=['GET'])
def get_all_job():
    database = db.SessionLocal()  # Create a new database session
    try:
        jobs = services.get_all_job(database)
        return jsonify({
            'status': True,
            'data': [job.serialize() for job in jobs]
        })
    finally:
        database.close()  # Always close the session after use
    
    
    