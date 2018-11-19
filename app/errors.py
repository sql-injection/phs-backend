from flask import jsonify
from enum import IntEnum


class ErrorCodes(IntEnum):
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500
    NOT_FOUND = 404
    UNAUTHORIZED = 401


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
