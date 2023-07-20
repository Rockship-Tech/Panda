import os
import sentry_sdk

from flask import Flask
from flask_cors import CORS

# from flasgger import Swagger
from sentry_sdk.integrations.flask import FlaskIntegration

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)  # Load env before run powerpaint


def create_app():
    app = Flask(__name__)
    from .blueprint.jobs.routes import jobs as jobs_router

    app.register_blueprint(jobs_router)

    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])

    CORS(app, resources={r"/*": {"origins": "*"}}, expose_headers=["X-Total-Count"])

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
