from flask import jsonify, Response


def ok(body):
    if isinstance(body, Response):
        body = body.get_json()

    return jsonify({
        "meta": {
            "status_code": 200,
            "message": "ok"
        },
        "response": body
    })
