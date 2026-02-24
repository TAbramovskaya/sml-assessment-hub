import os
from dotenv import load_dotenv


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(CUR_DIR, "..", "secret", "db_secrets.env")
load_dotenv(ENV_PATH)

ADMIN_POSTGRES_CONFIG = {
    "dbname": "postgres",
    "user": os.getenv("DB_ADMIN_USER"),
    "password": os.getenv("DB_ADMIN_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

ADMIN_DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "sml-assessment-hub"),
    "user": os.getenv("DB_ADMIN_USER"),
    "password": os.getenv("DB_ADMIN_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

USER_DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "sml-assessment-hub"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

SCHEMA_NAME = os.getenv("SCHEMA_NAME", "app")
SCHEMA_PLACEHOLDER = "<schema_name>"