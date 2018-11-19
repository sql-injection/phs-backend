import os
import re
import argparse
from load_csv import load_csv_into_db, DbCredentials, DataMeasureType


def main():
    """
    Walks through a given root directory and loads CSV files into a MySQL database. The root directory
    should contain patient data directories (e.g "patient1/")
    """
    parser = argparse.ArgumentParser(description="Load a CSV file into a MySQL database")
    parser.add_argument("--db", help="MySQL database name", required=True)
    parser.add_argument("--host", help="The host at which the database resides", required=True)
    parser.add_argument("--user", help="MySQL user that has database permissions", required=True)
    parser.add_argument("--password", help="MySQL password associated with --user", required=True)
    parser.add_argument("--root_data_dir",
                        help="The root directory that contains the patient data",
                        nargs="?",
                        default="data/")
    parser.add_argument("--patient_dir_pattern",
                        help="Regular expression pattern to find patient data directories",
                        nargs="?",
                        default=".+?patient(\d+).+?")

    args = parser.parse_args()
    credentials = DbCredentials(args.host, args.user, args.password, args.db)
    for subdir, dirs, files in os.walk(args.root_data_dir):
        for file in files:
            pattern = re.compile(args.patient_dir_pattern)
            m = re.match(pattern, subdir)

            if ".csv" not in file:
                continue

            if not m or not m.group(1):
                raise ValueError("Could not find patient directory with pattern: %s" % args.patient_dir_pattern)

            patient_id = m.group(1)
            file_path = os.path.join(subdir, file)

            if "HeartRate" in file:
                data_measure_type = DataMeasureType.HEART_RATE
            elif "ActivityRawType" in file:
                data_measure_type = DataMeasureType.ACTIVITY_TYPE
            elif "Steps" in file:
                data_measure_type = DataMeasureType.STEPS
            else:
                raise ValueError("Could not find valid measure in .csv file %s" % file)

            load_csv_into_db(credentials, file_path, data_measure_type, patient_id)


if __name__ == "__main__":
    main()