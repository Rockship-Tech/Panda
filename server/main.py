import os
import sentry_sdk

from flask import Flask
from flask_cors import CORS
# from flasgger import Swagger
from sentry_sdk.integrations.flask import FlaskIntegration

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)  # Load env before run powerpaint

# from system.exceptions import register_error_handlers
# from system.model_encoder import AlchemyEncoder
# from system.model_base import Session




def create_app():
    app = Flask(__name__)
    # swagger = Swagger(app)
    from .blueprint.jobs.routes import jobs as jobs_router

    app.register_blueprint(jobs_router)


    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()]
    )

    CORS(
        app,
        resources={
            r"/*": {
                'origins': '*'
            }
        },
        expose_headers=["X-Total-Count"]
    )

    # if os.getenv('ENV') and os.getenv('ENV') != 'PROD': 
        # Swagger(app, template=SWAGGER_CONFIG)

    print(os.environ.get('SQLALCHEMY_DATABASE_URI'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # app.json_encoder = AlchemyEncoder
    # register_error_handlers(app)
    # app.sess = Session()

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     Session.remove()
    #     if exception and Session.is_active:
    #         Session.rollback()

    
    @app.route('/')
    def hello():
        # Test the database connection
        try:
            # Create a session and execute a simple query to check the connection
            from .model import db
            db.get_db()
            
            return 'Successfully connected to the database!'
        except Exception as e:
            return f'Error: {str(e)}'



    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    
    
