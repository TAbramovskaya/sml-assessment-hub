import psycopg
import re
from logger import get_general_logger
from db.config import USER_DB_CONFIG, SCHEMA_NAME, SCHEMA_PLACEHOLDER

log = get_general_logger(__name__)


def apply_schema():
    """
    Apply the database schema from the SQL file db/schema.sql to the target database.
    """
    try:
        with psycopg.connect(**USER_DB_CONFIG) as conn:
            with conn.cursor() as cur:
                try:
                    with open("db/schema.sql") as f:
                        sql_text = f.read()
                except FileNotFoundError:
                    log.error("Schema file 'db/schema.sql' not found.")
                    raise

                # Validate schema name manually because this SQL is loaded from a file
                # and the schema name is substituted using string replacement, not psycopg.sql.Identifier
                if _validate_schema_name():
                    sql_text = sql_text.replace(SCHEMA_PLACEHOLDER, SCHEMA_NAME)
                try:
                    cur.execute(sql_text)
                except psycopg.Error as e:
                    log.error(f"SQL execution error: {e}")
                    raise
            conn.commit()
            log.info(f"Schema 'db/schema.sql' applied")

    except psycopg.Error as e:
        log.error(f"Database {USER_DB_CONFIG['name']} connection error: {e}")
        raise


def _validate_schema_name():
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", SCHEMA_NAME):
        raise ValueError(f"Invalid schema name: {SCHEMA_NAME}")

    return True