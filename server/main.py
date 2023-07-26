import os

# import sentry_sdk

from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine

# from flasgger import Swagger
from sentry_sdk.integrations.flask import FlaskIntegration

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)  # Load env before run powerpaint

# Access the value of PYTHONPATH
python_path = os.getenv("PYTHONPATH")

# Add PYTHONPATH to sys.path to handle modules
import sys

sys.path.append(python_path)


def test_database_connection():
    try:
        # Replace the placeholders with your actual database credentials
        db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI")
        engine = create_engine(db_uri)
        with engine.connect():
            print("Database connection successful!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")


def create_app():
    app = Flask(__name__)
    from .blueprint.job_routes import jobs as jobs_router
    from .blueprint.candidates_routes import candidates as candidates_router

    app.register_blueprint(jobs_router)
    app.register_blueprint(candidates_router)
    # sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])

    # CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers=["X-Total-Count"])

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    test_database_connection()  # Test the database connection

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
