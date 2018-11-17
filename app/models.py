import argparse, sys
from app import db
from sqlalchemy.ext.declarative import declared_attr

# Mixins
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
        return db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)


# Models
class Patient(Human, db.Model):
    birth_date = db.Column(db.Date, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    doctor = db.relationship('Doctor', backref=db.backref('patient', lazy=True))
    heart_rate_measures = db.relationship('HeartRate', backref='patient', lazy=True)
    step_measures = db.relationship('Steps', backref='patient', lazy=True)

    def __init__(self, first_name, last_name):
        Human.__init__(self, first_name, last_name)


class Doctor(Human, db.Model):
    def __init__(self, first_name, last_name):
        Human.__init__(self, first_name, last_name)


class Medication(Id, db.Model):
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    prescription = db.Column(db.String(255))


class HeartRate(PatientTimeSeriesMeasure, db.Model):
    heart_rate_measure = db.Column(db.Float, nullable=False)


class Steps(PatientTimeSeriesMeasure, db.Model):
    num_steps = db.Column(db.Integer, nullable=False)


class ActivityType(PatientTimeSeriesMeasure, db.Model):
    activity_type = db.Column(db.Integer, nullable=False)


def main():
    parser = argparse.ArgumentParser(description="Manage SQLAlchemy models")
    parser.add_argument("--create_all", action="store_true", help="Create all models", required=False)
    parser.add_argument("--nuke", action="store_true", help="Drop all previously created", required=False)
    args = parser.parse_args()
    if args.create_all and args.nuke:
        print("Error: Cannot both create and drop all models\n")
        parser.print_help()
        sys.exit(2)

    if args.create_all:
        print("Creating tables...")
        db.create_all()
        print("Done.")

    if args.nuke:
        print("Dropping tables...")
        db.drop_all()
        print("Done.")


if __name__ == "__main__":
    main()
