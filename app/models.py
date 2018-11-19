from app import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from flask import jsonify


class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Id(object):
    id = db.Column(db.Integer, primary_key=True)


class Human(Id):
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


class PatientTimeSeriesMeasure(object):
    unix_timestamp = db.Column(db.BigInteger, nullable=False, primary_key=True)

    @declared_attr
    def patient_id(self):
        return db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, primary_key=True)


patient_medication = db.Table('patient_medication',
                              db.Column("patient_id", db.Integer, db.ForeignKey(
                                  "patient.id"), primary_key=True),
                              db.Column("medication_id", db.Integer, db.ForeignKey(
                                  "medication.id"), primary_key=True),
                              db.Column("prescription", db.Text(length=500))
                              )

message = db.Table('message',
                    db.Column("patient_id", db.Integer, db.ForeignKey(
                        "patient.id"), primary_key=True),
                    db.Column("doctor_id", db.Integer, db.ForeignKey(
                        "medication.id"), primary_key=True),
                    db.Column("message_text", db.Text(length=500)),
                    db.Column("date_sent", db.Date),
                    db.Column("from_patient", db.Boolean)
                    )


class Medication(Id, db.Model, Serializer):
    name = db.Column(db.String(100))
    description = db.Column(db.Text(length=500))


class Patient(Human, db.Model, Serializer):
    birth_date = db.Column(db.Date, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'doctor.id'), nullable=False)
    doctor = db.relationship(
        "Doctor", backref=db.backref("patients", lazy=True))
    heart_rate_measures = db.relationship(
        "HeartRate", backref=db.backref("patient", lazy=True))
    step_measures = db.relationship(
        "Steps", backref=db.backref("patient", lazy=True))
    medication = db.relationship(
        "Medication",
        secondary=patient_medication,
        lazy="subquery",
        backref=db.backref("patient", lazy=True)
    )
    messages = db.relationship(
        "Messages",
        secondary=message,
        lazy="subquery",
        backref=db.backref("patient", lazy=True)
    )

    def __init__(self, first_name, last_name):
        Human.__init__(self, first_name, last_name)

    def to_json(self):
        body = self.serialize()
        doctor = body["doctor"].serialize()
        del doctor["patients"]
        body["doctor"] = doctor
        body["birth_date"] = body["birth_date"].strftime("%Y:%m:%d")
        del body["doctor_id"]
        return jsonify(body)


class Doctor(Human, db.Model, Serializer):
    def __init__(self, first_name, last_name):
        Human.__init__(self, first_name, last_name)


class HeartRate(PatientTimeSeriesMeasure, db.Model, Serializer):
    heart_rate_measure = db.Column(db.Float, nullable=False)


class Steps(PatientTimeSeriesMeasure, db.Model, Serializer):
    num_steps = db.Column(db.Integer, nullable=False)


class ActivityType(PatientTimeSeriesMeasure, db.Model, Serializer):
    activity_type = db.Column(db.Integer, nullable=False)


def main():
    db.create_all()


if __name__ == "__main__":
    main()
