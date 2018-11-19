from flask import jsonify


class ApiError(object):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def to_json(self):
        return jsonify({
            "meta": {
                "status_code": self.status_code,
                "message": self.message
            }
        })
