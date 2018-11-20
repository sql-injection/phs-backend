# personal health systems backend

### Functions

* Retrieving patient data within a unix timestamp window
    * POST `/patient/<patient_first_name>/<patient_last_name>?start=<start_timestamp>&end=<end_timestamp>`

### Local development
#### Program Requirements
* Python 3.6.*
* MySQL 5.6.*
* Pip

#### Installation
* Clone this repo: `git clone https://github.com/sql-injection/phs-backend.git`
* `cd phs-backend/`
* `pip install -r ./requirements.txt --no-cache-dir`
* Create a `.env` file in the root project directory, containing:

| environment variable  | definition                                                         | required | value                 | default      |
|-----------------------|--------------------------------------------------------------------|----------|-----------------------|--------------|
| `FLASK_ENV`           | Flask environment mode                                             | True     | "development"         | "production" |
| `FLASK_APP`           | Root file of the project                                           | True     | "app/app.py"          | None         |
| `DEVELOPMENT_DB_USER` | Username that has all permissions to your MySQL database instance  | False    | <your_mysql_username> | "test_user"  |
| `DEVELOPMENT_DB_PASSWORD`| Password associated with MySQL user | False | <your_mysql_password> | "test_password" |
| `DEVELOPMENT_DB_NAME` | Name of your local MySQL database | False | <your_mysql_db_name> | "phs_backend"
| `DEVELOPMENT_DB_HOST` | Where your db lives | False | <your_local_host> | "localhost"
| `DEVELOPMENT_DB_PORT` | Port at which your db lives | False | <your_local_port> | 3306

* Set up MySQL:
    * Run MySQL daemon
    * Set up a local test MySQL user
        * `mysql -u root -p`
        * `create database phs_backend;`
        * `use phs_backend;`
        * Grant permissions to a new user: `grant all PRIVILEGES on *.* to 'test_user'@'localhost' identified by 'test_password';`
        * Log out (Ctrl+D) and log in to test your newly created user: `mysql -u test_user -p`.
* Load models 
    * `python app/models.py`
* Load patients and doctors
    * `python scripts/load_dummy_data.py --db <db_name> --host localhost --user <username> --password <password>`
* Load in patient CSVs
    * `python scripts/load_all_patient_csvs.py --db <db_name> --host localhost --user <username> --password <password>`
* Start a local server
    * `python -m flask run`
    
   
