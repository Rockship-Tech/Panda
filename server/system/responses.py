from flask import jsonify


class Responses:
    def __init__(self, context=None):
        self.context = context

    def success_response(self, data=None, status_code=200):
        response = {
            "apiVersion": "1.0",
            "context": self.context,
            "data": data,
        }
        return jsonify(response), status_code

    def error_response(self, message, status_code):
        response = {
            "apiVersion": "1.0",
            "context": self.context,
            "error": {
                "code": status_code,
                "message": message,
            },
        }
        return jsonify(response), status_code

    def not_found_response(self):
        return self.error_response("Not Found", 404)

    def bad_request_response(self, message):
        return self.error_response(message, 400)

    def internal_server_error_response(self):
        return self.error_response("Internal Server Error", 500)
