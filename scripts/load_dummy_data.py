import argparse
import pymysql
import pymysql.cursors


def main():
    parser = argparse.ArgumentParser(
        description="Load mock patients and doctors into a MySQL database")
    parser.add_argument("--db", help="MySQL database name", required=True)
    parser.add_argument(
        "--host", help="The host at which the database resides", required=True)
    parser.add_argument(
        "--user", help="MySQL user that has database permissions", required=True)
    parser.add_argument(
        "--password", help="MySQL password associated with --user", required=True)
    args = parser.parse_args()

    doctors = [
        dict(id=1, first_name="Nikolaos", last_name="Maglaveras"),
        dict(id=2, first_name="Ilya", last_name="Mikhelson")
    ]

    patients = [
        dict(id=1, first_name="Fabian", last_name="Bustamante",
             birth_date="1950-10-11", doctor_id=1),
        dict(id=2, first_name="Robby", last_name="Findler",
             birth_date="1960-12-05", doctor_id=1),
        dict(id=3, first_name="Ian", last_name="Horswill",
             birth_date="1969-4-20", doctor_id=1),
        dict(id=4, first_name="Sara", last_name="Sood",
             birth_date="1980-5-28", doctor_id=1),
        dict(id=5, first_name="Bryan", last_name="Pardo",
             birth_date="1990-5-15", doctor_id=1),
        dict(id=6, first_name="Doug", last_name="Downey",
             birth_date="1971-1-09", doctor_id=2),
        dict(id=7, first_name="Christopher", last_name="Riesbeck",
             birth_date="1961-1-11", doctor_id=2),
        dict(id=8, first_name="Brenna", last_name="Argall",
             birth_date="1968-8-20", doctor_id=2),
        dict(id=9, first_name="Jason", last_name="Hartline",
             birth_date="1965-9-11", doctor_id=2)
    ]

    diseases = [
        dict(id=1, name="Myocarditis", url="https://rarediseases.info.nih.gov/diseases/7137/myocarditis"),
        dict(id=2, name="Supraventricular Tachycardia ", url="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4295736/"),
        dict(id=3, name="Tetralogy of Fallot", url="https://rarediseases.info.nih.gov/diseases/2245/tetralogy-of-fallot"),
        dict(id=4, name="Congenital Mitral Stenosis", url="https://www.cdc.gov/ncbddd/heartdefects/hlhs.html"),
        dict(id=5, name="Long QT Syndrome", url="https://rarediseases.info.nih.gov/diseases/6922/long-qt-syndrome"),
        dict(id=6, name="Atrial flutter", url="https://www.cdc.gov/dhdsp/data_statistics/fact_sheets/fs_atrial_fibrillation.htm"),
        dict(id=7, name="Wolf-Parkinson-White Syndrome", url="https://rarediseases.info.nih.gov/diseases/7897/wolff-parkinson-white-syndrome"),
        dict(id=7, name="Atrial Fibrillation", url="https://www.cdc.gov/dhdsp/data_statistics/fact_sheets/fs_atrial_fibrillation.htm"),
        dict(id=8, name="Ventricular Tachycardia", url="https://stanfordhealthcare.org/medical-conditions/blood-heart-circulation/ventricular-tachycardia.html"),
        dict(id=9, name="Endocarditis", url="https://www.webmd.com/heart-disease/what-is-endocarditis#1"),
        dict(id=10, name="Congestive Heart Failure", url="https://www.cdc.gov/dhdsp/data_statistics/fact_sheets/fs_heart_failure.htm")
    ]

    medications = [
        dict(id=1, name="Milrinone", url="https://www.rxlist.com/primacor-iv-drug.htm#precautions",
             notes="https://medlineplus.gov/ency/patientinstructions/000112.htm"),
        dict(id=2, name="Verapamil", url="https://medlineplus.gov/druginfo/meds/a684030.html"),
        dict(id=3, name="Propanolol", url="https://medlineplus.gov/druginfo/meds/a682607.html"),
        dict(id=4, name="Procainamide", url="https://medlineplus.gov/druginfo/meds/a682398.html"),
        dict(id=5, name="Amiodarone", url="https://medlineplus.gov/druginfo/meds/a687009.html"),
        dict(id=6, name="Antibiotics", url="https://medlineplus.gov/antibiotics.html"),
        dict(id=7, name="Digoxin", url="https://medlineplus.gov/druginfo/meds/a682301.html")
    ]

    patient_medications = [
        dict(patient_id=1, medication_id=1, dosage_amount=20, dosage_measure="mg", dosage_instructions=None,
             notes=None),
        dict(patient_id=2, medication_id=2, dosage_amount=180, dosage_measure="mg/24hr", dosage_instructions=None,
             notes=None),
        dict(patient_id=3, medication_id=3, dosage_amount=180, dosage_measure="mg/24hr", dosage_instructions=None,
             notes=None),
        dict(patient_id=4, medication_id=4, dosage_amount=250, dosage_measure="mg", dosage_instructions=None,
             notes=None),
        dict(patient_id=5, medication_id=5, dosage_amount=50, dosage_measure="mg", dosage_instructions=None,
             notes=None),
        dict(patient_id=6, medication_id=6, dosage_amount=500, dosage_measure="mg", dosage_instructions=None,
             notes=None),
        dict(patient_id=7, medication_id=7, dosage_amount=20, dosage_measure="mg", dosage_instructions=None,
             notes=None),
        dict(patient_id=8, medication_id=1, dosage_amount=20, dosage_measure="mg", dosage_instructions=None,
             notes=None),
        dict(patient_id=9, medication_id=1, dosage_amount=20, dosage_measure="mg", dosage_instructions=None,
             notes=None)
    ]

    patient_diseases = [
        dict(patient_id=1, disease_id=1),
        dict(patient_id=2, disease_id=2),
        dict(patient_id=3, disease_id=3),
        dict(patient_id=4, disease_id=4),
        dict(patient_id=5, disease_id=5),
        dict(patient_id=6, disease_id=6),
        dict(patient_id=7, disease_id=7),
        dict(patient_id=8, disease_id=8),
        dict(patient_id=9, disease_id=9)
    ]

    connection = pymysql.connect(
        host=args.host,
        user=args.user,
        password=args.password,
        db=args.db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            def patient_and_doctors():
                doctor_sql_statement = "INSERT IGNORE INTO doctor (id, first_name, last_name) VALUES"
                for index, doctor in enumerate(doctors):
                    doctor_sql_statement += "{} ({}, '{}', '{}')".format(
                        "," if index > 0 else "",
                        doctor["id"],
                        doctor["first_name"],
                        doctor["last_name"]
                    )

                cursor.execute(doctor_sql_statement)
                connection.commit()

                patient_sql_statement = """
                INSERT IGNORE INTO patient (id, first_name, last_name, birth_date, doctor_id) VALUES
                """

                for index, patient in enumerate(patients):
                    patient_sql_statement += "{} ({}, '{}', '{}', '{}', {})".format(
                        "," if index > 0 else "",
                        patient["id"],
                        patient["first_name"],
                        patient["last_name"],
                        patient["birth_date"],
                        patient["doctor_id"]
                    )

                cursor.execute(patient_sql_statement)
                connection.commit()

            def add_diseases():
                disease_sql_statement = "INSERT IGNORE INTO disease (id, name, url) VALUES"
                for index, disease in enumerate(diseases):
                    disease_sql_statement += "{} ({}, '{}', '{}')".format(
                        "," if index > 0 else "",
                        disease["id"],
                        disease["name"],
                        disease["url"]
                    )

                cursor.execute(disease_sql_statement)
                connection.commit()

            def add_medications():
                medication_sql_statement = "INSERT IGNORE INTO medication (id, name, url, notes) VALUES"
                for index, medication in enumerate(medications):
                    medication_sql_statement += "{} ({}, '{}', '{}', {})".format(
                        "," if index > 0 else "",
                        medication["id"],
                        medication["name"],
                        medication["url"],
                        "'{}'".format(medication["notes"]) if "notes" in medication else "NULL"
                    )

                cursor.execute(medication_sql_statement)
                connection.commit()

            def add_patient_meds():
                sql_statement = "INSERT IGNORE INTO patient_medication (patient_id, "\
                        "medication_id, dosage_amount, dosage_measure, dosage_instructions, notes) VALUES"
                for index, patient_medication in enumerate(patient_medications):
                    sql_statement += "{} ({}, {}, {}, '{}', {}, {})".format(
                        "," if index > 0 else "",
                        patient_medication["patient_id"],
                        patient_medication["medication_id"],
                        patient_medication["dosage_amount"],
                        patient_medication["dosage_measure"],
                        "'{}'".format(patient_medication["dosage_instructions"]) if "dosage_instructions" in patient_medication else "NULL",
                        "'{}'".format(patient_medication["notes"]) if "notes" in patient_medication else "NULL"
                    )

                cursor.execute(sql_statement)
                connection.commit()

            def add_patient_diseases():
                sql_statement = "INSERT IGNORE INTO patient_disease (patient_id, disease_id) VALUES"
                for index, patient_disease in enumerate(patient_diseases):
                    sql_statement += "{} ({}, {})".format(
                        "," if index > 0 else "",
                        patient_disease["patient_id"],
                        patient_disease["disease_id"]
                    )

                cursor.execute(sql_statement)
                connection.commit()

            patient_and_doctors()
            add_diseases()
            add_medications()
            add_patient_meds()
            add_patient_diseases()

    finally:
        connection.close()


if __name__ == "__main__":
    main()
