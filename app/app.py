from environs import Env
from marshmallow.validate import OneOf

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


env = Env()
env_mode = env.str(
    "FLASK_ENV",
    default="development",
    validate=OneOf(
        ["production", "development"], error="FLASK_ENV must be one of: {choices}"
    ),
).upper()


with env.prefixed(env_mode):
    with env.prefixed("_DB_"):
        db_user = env.str("USER", default="test_user")
        db_password = env.str("PASSWORD", default="test_password")
        db_host = env.str("HOST", default="localhost")
        db_port = env.int("PORT", default=3000)
        db_name = env.str("NAME", default="phs_backend")

db_uri = "mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}".format(
    db_user=db_user,
    db_password=db_password,
    db_host=db_host,
    db_port=db_port,
    db_name=db_name
)

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=db_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)


db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/")
def hello_world():
    return "Hello, world!"

