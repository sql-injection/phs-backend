import csv
import argparse
import pymysql
import pymysql.cursors
from load_csv import DbCredentials


def main():
    parser = argparse.ArgumentParser(description="Generate RR dataset from MySQL database")
    parser.add_argument("--db", help="MySQL database name", required=True)
    parser.add_argument("--host", help="The host at which the database resides", required=True)
    parser.add_argument("--user", help="MySQL user that has database permissions", required=True)
    parser.add_argument("--password", help="MySQL password associated with --user", required=True)
    parser.add_argument("--output_file", help="Name of output CSV file", required=True)

    args = parser.parse_args()
    credentials = DbCredentials(args.host, args.user, args.password, args.db)
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
            sql_statement = "SELECT p.id, h.unix_timestamp, h.heart_rate_measure as bpm, h.rr FROM heart_rate h "\
                            "INNER JOIN patient p ON h.patient_id = p.id"
            cursor.execute(sql_statement)
            result = cursor.fetchall()

            with open(args.output_file, 'w') as f:
                keys = result[0].keys()
                dict_writer = csv.DictWriter(f, keys)
                dict_writer.writeheader()
                dict_writer.writerows(result)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
