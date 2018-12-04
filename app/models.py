from app import db, env
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.mysql import BIGINT
from flask import jsonify


class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

    def to_json(self):
        body = self.serialize()
        return jsonify(body)


class Id(object):
    id = db.Column(db.Integer, primary_key=True)


class Human(Id):
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


class PatientTimeSeriesMeasure(object):
    unix_timestamp = db.Column(BIGINT(unsigned=True), nullable=False, primary_key=True)

    @declared_attr
    def patient_id(self):
        return db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, primary_key=True)


patient_medication = db.Table("patient_medication",
                              db.Column("patient_id", db.Integer, db.ForeignKey(
                                  "patient.id"), primary_key=True),
                              db.Column("medication_id", db.Integer, db.ForeignKey(
                                  "medication.id"), primary_key=True),
                              db.Column("dosage_amount", db.Float, nullable=False),
                              db.Column("dosage_measure", db.String(100), nullable=False),
                              db.Column("dosage_instructions", db.Text(length=500), nullable=False),
                              db.Column("notes", db.Text(length=500))
                              )

patient_disease = db.Table("patient_disease",
                           db.Column("patient_id", db.Integer, db.ForeignKey(
                                "patient.id"), primary_key=True),
                           db.Column("disease_id", db.Integer, db.ForeignKey(
                                "disease.id"), primary_key=True))


class Message(Id, db.Model, Serializer):
    patient_id = db.Column(db.Integer, db.ForeignKey(
        "patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        "doctor.id"), nullable=False)
    message_text = db.Column(db.Text(length=500))
    date_sent = db.Column(db.BigInteger)
    from_patient = db.Column(db.Boolean)


class Medication(Id, db.Model, Serializer):
    name = db.Column(db.String(100))
    notes = db.Column(db.Text(length=500), nullable=True)
    url = db.Column(db.String(255))


class Disease(Id, db.Model, Serializer):
    name = db.Column(db.String(100))
    notes = db.Column(db.Text(length=500), nullable=True)
    url = db.Column(db.String(255))


class Patient(Human, db.Model, Serializer):
    birth_date = db.Column(db.Date, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'doctor.id'), nullable=False)
    doctor = db.relationship("Doctor")
    heart_rate_measures = db.relationship(
        "HeartRate", lazy="dynamic", cascade="all, delete-orphan")
    step_measures = db.relationship(
        "Steps", lazy="dynamic", cascade="all, delete-orphan")
    activity_type_measures = db.relationship(
        "ActivityType", lazy="dynamic", cascade="all, delete-orphan")
    medications = db.relationship(
        "Medication",
        secondary=patient_medication,
        lazy="subquery"
    )
    diseases = db.relationship(
        "Disease",
        secondary=patient_disease,
        lazy="subquery"
    )
    messages = db.relationship("Message", lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, first_name, last_name):
        Human.__init__(self, first_name, last_name)

    def serialize(self):
        body = super(Patient, self).serialize()
        body["doctor"] = body["doctor"].serialize()
        body["birth_date"] = body["birth_date"].strftime("%Y:%m:%d")
        heart_rates = self.serialize_list(body["heart_rate_measures"])
        steps = self.serialize_list(body["step_measures"])
        activity_types = self.serialize_list(body["activity_type_measures"])
        medications = self.serialize_list(body["medications"])
        diseases = self.serialize_list(body["diseases"])
        messages = self.serialize_list(body["messages"])

        body["heart_rate_measures"] = heart_rates
        body["step_measures"] = steps
        body["activity_type_measures"] = activity_types
        body["medications"] = medications
        body["messages"] = messages
        body["diseases"] = diseases

        del body["doctor_id"]
        return body


class Doctor(Human, db.Model, Serializer):
    def __init__(self, first_name, last_name):
        Human.__init__(self, first_name, last_name)


class HeartRate(PatientTimeSeriesMeasure, db.Model, Serializer):
    heart_rate_measure = db.Column(db.Float, nullable=False)
    rr = db.Column(db.Float, nullable=False)


class Steps(PatientTimeSeriesMeasure, db.Model, Serializer):
    num_steps = db.Column(db.Integer, nullable=False)


class ActivityType(PatientTimeSeriesMeasure, db.Model, Serializer):
    activity_type = db.Column(db.Integer, nullable=False)


def main():
    db.create_all()


if __name__ == "__main__":
    main()
