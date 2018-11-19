import csv
import sys
import pymysql
import pymysql.cursors
from enum import Enum


class DataMeasureType(Enum):
    """ Different kinds of data measures """
    HEART_RATE = 1
    ACTIVITY_TYPE = 2
    STEPS = 3


class DbCredentials(object):
    """ Class that contains all required database login information """
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name


def load_csv_into_db(credentials, file_path, data_measure_type, patient_id):
    """
    Constructs and attempts to commit a SQL transaction to insert every row of a patient time-series
    CSV file into a MySQL database
    """
    with open(file_path) as f:
        csv_data = csv.reader(f)
        data = [(int(row[0]) // 1000, float(row[1])) for row in csv_data]

    connection = pymysql.connect(
        host=credentials.host,
        user=credentials.user,
        password=credentials.password,
        db=credentials.db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            if data_measure_type == DataMeasureType.HEART_RATE:
                sql_statement = "INSERT IGNORE INTO heart_rate (unix_timestamp, heart_rate_measure, patient_id) VALUES"
                for index, row in enumerate(data):
                    timestamp, measure = row
                    sql_statement += "{} ({}, {}, {})".format(
                        "," if index > 0 else "",
                        timestamp,
                        measure,
                        patient_id
                    )
                cursor.execute(sql_statement)
                connection.commit()
            elif data_measure_type == DataMeasureType.ACTIVITY_TYPE:
                sql_statement = "INSERT IGNORE INTO activity_type (unix_timestamp, activity_type, patient_id) VALUES"
                for index, row in enumerate(data):
                    timestamp = row[0]
                    activity_type = int(row[1])
                    sql_statement += "{} ({}, {}, {})".format(
                        "," if index > 0 else "",
                        timestamp,
                        activity_type,
                        patient_id
                    )
                cursor.execute(sql_statement)
                connection.commit()
            elif data_measure_type == DataMeasureType.STEPS:
                sql_statement = "INSERT IGNORE INTO steps (unix_timestamp, num_steps, patient_id) VALUES"
                for index, row in enumerate(data):
                    timestamp = row[0]
                    num_steps = int(row[1])
                    sql_statement += "{} ({}, {}, {})".format(
                        "," if index > 0 else "",
                        timestamp,
                        num_steps,
                        patient_id
                    )
                cursor.execute(sql_statement)
                connection.commit()
            else:
                sys.exit(2)

    finally:
        connection.close()
