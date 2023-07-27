from flask import jsonify


class Responses:
    def __init__(self, context=None):
        self.context = context


class SuccessResponse(Responses):
    def generate_response(self, data=None, status_code=200):
        response = {
            "apiVersion": "1.0",
            "context": self.context,
            "data": data,
        }
        return jsonify(response), status_code


class ErrorResponse(Responses):
    def generate_response(self, message, status_code, errors=None):
        response = {
            "apiVersion": "1.0",
            "context": self.context,
            "error": {
                "code": status_code,
                "message": message,
                "errors": errors if errors is not None else [],
            },
        }
        return jsonify(response), status_code

    def not_found_response(self):
        return self.generate_response("Not Found", 404)

    def bad_request_response(self, message, errors=None):
        error_details = [
            {
                "domain": "",
                "reason": "invalidInput",
                "message": message,
                "location": "",
                "locationType": "",
            }
        ]
        return self.generate_response("Bad Request", 400, error_details)

    def internal_server_error_response(self):
        return self.generate_response("Internal Server Error", 500)
