import os
import time
from environs import Env
from marshmallow.validate import OneOf
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


env = Env()
env.read_env()

env_mode = env.str(
    "FLASK_ENV",
    default="development",
    validate=OneOf(
        ["production", "development"], error="FLASK_ENV must be one of: {choices}"
    ),
).upper()

with env.prefixed(env_mode):
    with env.prefixed("_DB_"):
        db_user = env.str("USER", default="test_user")
        db_password = env.str("PASSWORD", default="test_password")
        db_host = env.str("HOST", default="localhost")
        db_port = env.int("PORT", default=3306)
        db_name = env.str("NAME", default="phs_backend")

db_uri = "mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}".format(
    db_user=db_user,
    db_password=db_password,
    db_host=db_host,
    db_port=db_port,
    db_name=db_name
)

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=db_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)


MIGRATION_DIR = os.path.join('app', 'migrations')
db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=MIGRATION_DIR)


@app.route("/")
def hello_world():
    return "Hello, world!"


@app.route("/patient/<last_name>/<first_name>", methods=["GET"])
def get_patient(last_name, first_name):
    from models import Patient
    from sqlalchemy import func
    from tools import ok
    patient = Patient.query.filter(
        func.lower(Patient.last_name) == func.lower(last_name) and
        func.lower(Patient.first_name) == func.lower(first_name)
    ).first_or_404()
    return ok(patient.to_json())


@app.route("/patient/<last_name>/<first_name>", methods=["POST"])
def get_patient_data_in_time_window(last_name, first_name):
    from models import Patient, ActivityType, HeartRate, Steps
    from sqlalchemy import func
    from errors import ApiError, ErrorCodes
    from tools import ok

    start_unix_time = request.args.get("start")
    end_unix_time = request.args.get("end")
    print(start_unix_time, end_unix_time)

    if not start_unix_time or not end_unix_time:
        return ApiError(status_code=ErrorCodes.BAD_REQUEST,
                        message="Must include unix timestamps in query parameters start and end.").to_json()

    try:
        start_unix_time = int(start_unix_time)
        end_unix_time = int(end_unix_time)
    except ValueError:
        return ApiError(status_code=ErrorCodes.BAD_REQUEST,
                        message="Unix timestamps given in start and end must be integers").to_json()
    finally:
        patient = db.session.query(Patient).filter(
            func.lower(Patient.last_name) == func.lower(last_name) and
            func.lower(Patient.first_name) == func.lower(first_name)
        ).first()

        activity_measures = patient.activity_type_measures.filter(
            (ActivityType.unix_timestamp >= start_unix_time) & (ActivityType.unix_timestamp <= end_unix_time)
        ).all()
        heart_rates = patient.heart_rate_measures.filter(
            (HeartRate.unix_timestamp >= start_unix_time) & (HeartRate.unix_timestamp <= end_unix_time)
        ).all()
        steps = patient.step_measures.filter(
            (Steps.unix_timestamp >= start_unix_time) & (Steps.unix_timestamp <= end_unix_time)
        ).all()

        patient.activity_type_measures = activity_measures
        patient.heart_rate_measures = heart_rates
        patient.step_measures = steps
        return ok(patient.to_json())


@app.route("/message", methods=["POST"])
def send_message():
    from models import Patient, Doctor, Message
    from errors import ApiError, ErrorCodes
    from tools import ok

    request_body = request.json
    patient_id = request_body["patient_id"]
    doctor_id = request_body["doctor_id"]
    from_patient = request_body["from_patient"]
    message_text = request_body["message_text"]

    patient = db.session.query(Patient).filter(Patient.id == patient_id).first()
    doctor = db.session.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not patient or not doctor:
        return ApiError(status_code=ErrorCodes.BAD_REQUEST,
                        message="Patient or doctor does not exist. Unable to send message").to_json()

    message = Message()
    message.date_sent = int(time.time())
    message.from_patient = from_patient
    message.message_text = message_text
    message.doctor_id = doctor_id
    message.patient_id = patient_id

    patient.messages.append(message)
    db.session.commit()

    return ok(message.to_json())


@app.route("/patient/<last_name>/<first_name>/metrics", methods=["POST"])
def compute_health_metrics_by_day(last_name, first_name):
    from models import Patient, ActivityType, HeartRate, Steps
    from sqlalchemy import func
    from errors import ApiError, ErrorCodes
    from tools import ok

    patient = db.session.query(Patient).filter(
        func.lower(Patient.last_name) == func.lower(last_name) and
        func.lower(Patient.first_name) == func.lower(first_name)
    ).first()

    return ok(patient.to_json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


