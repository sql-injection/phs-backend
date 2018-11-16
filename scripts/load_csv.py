import argparse
import csv
import sys
import pymysql
import pymysql.cursors


def main():
    parser = argparse.ArgumentParser(description="Load a CSV file into a MySQL database")
    parser.add_argument("--csv", help="Path to CSV to load into MySQL database", required=True)
    parser.add_argument("--db", help="MySQL database name", required=True)
    parser.add_argument("--type",
                        help="Personal health systems file type",
                        choices=["hr", "activity", "steps"],
                        required=True)
    parser.add_argument("--user", help="MySQL user that has database permissions", required=True)
    parser.add_argument("--password", help="MySQL password associated with --user", required=True)
    parser.add_argument("--patient_id", help="Patient id associated with data", required=True)
    args = parser.parse_args()

    with open(args.csv) as f:
        csv_data = csv.reader(f)
        data = [(int(row[0]) // 1000, float(row[1])) for row in csv_data]

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
            if args.type == "hr":
                sql_statement = "INSERT INTO heart_rate (unix_timestamp, heart_rate_measure, patient_id) VALUES"
                for index, row in enumerate(data):
                    timestamp, measure = row
                    sql_statement += "{} ({}, {}, {})".format(
                        "," if index > 0 else "",
                        timestamp,
                        measure,
                        args.patient_id
                    )
                cursor.execute(sql_statement)
                connection.commit()
            elif args.type == "activity":
                sql_statement = "INSERT INTO activity_type (unix_timestamp, activity_type, patient_id) VALUES"
                for index, row in enumerate(data):
                    timestamp = row[0]
                    activity_type = int(row[1])
                    sql_statement += "{} ({}, {}, {})".format(
                        "," if index > 0 else "",
                        timestamp,
                        activity_type,
                        args.patient_id
                    )
                cursor.execute(sql_statement)
                connection.commit()
            elif args.type == "steps":
                return
            else:
                sys.exit(2)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
