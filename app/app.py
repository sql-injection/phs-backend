import os
import time
import numpy as np
from environs import Env
from threading import Thread
from marshmallow.validate import OneOf
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from lib.timeDomain import timeDomain
from lib.multiScaleEntropy import sampEn
from lib.DFA import scalingExponent
from lib.poincare import correlation_coef, eclipse_fitting_methods

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

CORS(app)
MIGRATION_DIR = os.path.join('app', 'migrations')
db = SQLAlchemy(app)
migrate = Migrate(app, db, directory=MIGRATION_DIR)




@app.route("/")
def hello_world():
    return "Hello, world!"


@app.route("/patient/all", methods=["GET"])
def get_patients():
    from models import Patient
    from tools import ok

    patients = Patient.query.with_entities(Patient.id, Patient.first_name, Patient.last_name, Patient.birth_date).all()
    body = dict()
    body["patients"] = patients
    return ok(body)


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
            (ActivityType.unix_timestamp >= start_unix_time) & (
                ActivityType.unix_timestamp <= end_unix_time)
        ).all()
        heart_rates = patient.heart_rate_measures.filter(
            (HeartRate.unix_timestamp >= start_unix_time) & (
                HeartRate.unix_timestamp <= end_unix_time)
        ).all()
        steps = patient.step_measures.filter(
            (Steps.unix_timestamp >= start_unix_time) & (
                Steps.unix_timestamp <= end_unix_time)
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

    patient = db.session.query(Patient).filter(
        Patient.id == patient_id).first()
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


@app.route("/patient/<patient_id>/messages", methods=["GET"])
def get_all_messages(patient_id):
    from models import Message
    from tools import ok

    messages = db.session.query(Message).filter(
        Message.patient_id == patient_id)
    messages = Message.serialize_list(messages)
    return ok(messages)


@app.route("/patient/<patient_id>/metrics", methods=["GET"])
def compute_health_metrics_in_time_window(patient_id):
    from models import HeartRate
    from errors import ApiError, ErrorCodes
    from tools import ok

    start_unix_time = request.args.get("start")
    end_unix_time = request.args.get("end")

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
        print(patient_id, start_unix_time, end_unix_time)
        payload = dict()

        # Produce a list of RR intervals based on time window
        rr_list = db.session.query(HeartRate).filter(
            (HeartRate.patient_id == patient_id) &
            (HeartRate.unix_timestamp >= start_unix_time) &
            (HeartRate.unix_timestamp <= end_unix_time)
        ).with_entities(HeartRate.rr).all()
        rrs = [rr for rr_sublist in rr_list for rr in rr_sublist]

        if len(rrs) < 1:
            return ApiError(
                status_code=ErrorCodes.BAD_REQUEST,
                message="Insufficient RR intervals in time window {} to {}".format(start_unix_time, end_unix_time)
            ).to_json()

        time_domain_measures = dict()
        non_linear_measures = dict()
        non_linear_measures["poincare"] = dict()

        def time_domain_worker():
            [ann, sdnn, p_nn50, p_nn20, r_mssd] = timeDomain(rrs)
            time_domain_measures["ann"] = ann
            time_domain_measures["sdnn"] = sdnn
            time_domain_measures["pnn50"] = p_nn50
            time_domain_measures["pnn20"] = p_nn20
            time_domain_measures["rmssd"] = r_mssd

        def sample_entropy_worker():
            try:
                r = 0.2 * np.std(rrs)
                non_linear_measures["sample_entropy"] = sampEn(rrs, 2, r)
            except ValueError:
                non_linear_measures["sample_entropy"] = 0.0

        def dfa_worker():
            non_linear_measures["dfa"] = dict()

            if len(rrs) > 0:
                upper_scale_limit = min(1000, len(rrs))
                [scales, f, alpha] = scalingExponent(
                    rrs, 5, upper_scale_limit, 20, 1, 2)

                non_linear_measures["dfa"]["scales"] = scales.tolist()
                non_linear_measures["dfa"]["fluctuation_coefficients"] = f.tolist(
                )
                non_linear_measures["dfa"]["alpha"] = alpha

        def poincare_coefficient():
            coefficient = correlation_coef(rrs)
            non_linear_measures["poincare"]["correlation_coefficient"] = coefficient

        def eclipse_fitting():
            standard_deviations = eclipse_fitting_methods(rrs)
            non_linear_measures["poincare"]["standard_deviations"] = dict()
            non_linear_measures["poincare"]["standard_deviations"]["sd1"] = standard_deviations["SD1"]
            non_linear_measures["poincare"]["standard_deviations"]["sd2"] = standard_deviations["SD2"]
            non_linear_measures["poincare"]["rr1"] = rrs[:-1]
            non_linear_measures["poincare"]["rr2"] = rrs[1:]

        t1 = Thread(target=time_domain_worker)
        t2 = Thread(target=sample_entropy_worker)
        t3 = Thread(target=dfa_worker)
        t4 = Thread(target=poincare_coefficient)
        t5 = Thread(target=eclipse_fitting)
        threads = [t1, t2, t3, t4, t5]
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()

        for thread in threads:
            thread.join()

        payload["time_domain_measures"] = time_domain_measures
        payload["non_linear_measures"] = non_linear_measures

        return ok(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
