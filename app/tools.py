from flask import jsonify


def ok(body):
    return jsonify({
        "meta": {
            "status_code": 200,
            "message": "ok"
        },
        "response": body.get_json()
    })
