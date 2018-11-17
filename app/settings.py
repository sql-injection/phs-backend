from environs import Env

env = Env()
env.read_env()


class Config(object):
    DEBUG = env.bool("DEBUG", True)
    TESTING = env.bool("TESTING", False)
    DB_USER = env.str("DB_USER", "test_user")
    DB_PASSWORD = env.str("DB_PASSWORD", "test_password")
    DB_NAME = env.str("DB_NAME", "phs_backend")
    DB_HOST = env.str("DB_HOST", "localhost")
    DB_PORT = env.int("DB_PORT", 3000)
