import argparse
import pymysql
import pymysql.cursors


def main():
    parser = argparse.ArgumentParser(description="Load mock patients and doctors into a MySQL database")
    parser.add_argument("--db", help="MySQL database name", required=True)
    parser.add_argument("--user", help="MySQL user that has database permissions", required=True)
    parser.add_argument("--password", help="MySQL password associated with --user", required=True)
    args = parser.parse_args()

    doctors = [
        dict(id=1, first_name="Nikolaos", last_name="Maglaveras"),
        dict(id=2, first_name="Ilya", last_name="Mikhelson")
    ]

    patients = [
        dict(id=1, first_name="Fabian", last_name="Bustamante", birth_date="1950-10-11", doctor_id=1),
        dict(id=2, first_name="Robby", last_name="Findler", birth_date="1960-12-05", doctor_id=1),
        dict(id=3, first_name="Ian", last_name="Horswill", birth_date="1969-4-20", doctor_id=1),
        dict(id=4, first_name="Sara", last_name="Sood", birth_date="1980-5-28", doctor_id=1),
        dict(id=5, first_name="Bryan", last_name="Pardo", birth_date="1990-5-15", doctor_id=1),
        dict(id=6, first_name="Doug", last_name="Downey", birth_date="1971-1-09", doctor_id=2),
        dict(id=7, first_name="Christopher", last_name="Riesbeck", birth_date="1961-1-11", doctor_id=2),
        dict(id=8, first_name="Brenna", last_name="Argall", birth_date="1968-8-20", doctor_id=2),
        dict(id=9, first_name="Jason", last_name="Hartline", birth_date="1965-9-11", doctor_id=2)
    ]

    connection = pymysql.connect(
        host='localhost',
        user=args.user,
        password=args.password,
        db=args.db,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
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
    finally:
        connection.close()


if __name__ == "__main__":
    main()
