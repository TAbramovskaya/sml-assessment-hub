import psycopg
from psycopg import sql
from logger import get_general_logger
from db.config import ADMIN_POSTGRES_CONFIG, ADMIN_DB_CONFIG, USER_DB_CONFIG, SCHEMA_NAME

log = get_general_logger(__name__)


def db_create_if_not_exist():
    """
    Create the database if it does not already exist.
    """
    with psycopg.connect(**ADMIN_POSTGRES_CONFIG, autocommit=True) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT 1 FROM pg_database WHERE datname = {};").format(
                        sql.Literal(USER_DB_CONFIG['dbname'])
                    )
                )
                if cur.fetchone():
                    log.info(f"Database {USER_DB_CONFIG['dbname']} already exists")
                else:
                    cur.execute(
                        sql.SQL("CREATE DATABASE {}").format(
                            sql.Identifier(USER_DB_CONFIG['dbname'])
                        )
                    )
                    log.info(f"Database {USER_DB_CONFIG['dbname']} created")

        except psycopg.OperationalError as e:
            log.error(f"Database {ADMIN_POSTGRES_CONFIG['dbname']} connection error: {e}")
            raise
        except psycopg.Error as e:
            log.error(f"Error creating database {USER_DB_CONFIG['dbname']}: {e}")
            raise


def user_create_if_not_exist():
    """
    Create the user if it does not already exist.
    """
    try:
        with psycopg.connect(**ADMIN_POSTGRES_CONFIG, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT 1 FROM pg_roles WHERE rolname = {};").format(
                        sql.Literal(USER_DB_CONFIG['user'])
                    )
                )
                if cur.fetchone():
                    log.info(f"User {USER_DB_CONFIG['user']} already exists")
                else:
                    cur.execute(
                        sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD {};").format(
                            sql.Identifier(USER_DB_CONFIG['user']),
                            sql.Literal(USER_DB_CONFIG['password'])
                        )
                    )
                    log.info(f"Role {USER_DB_CONFIG['user']} created successfully")

    except psycopg.OperationalError as e:
        log.error(f"Database {ADMIN_POSTGRES_CONFIG['dbname']} connection error: {e}")
        raise
    except psycopg.Error as e:
        log.error(f"Error creating role {USER_DB_CONFIG['user']}: {e}")
        raise


def schema_create_if_not_exists():
    """
    Create the schema if it does not already exist.
    The schema is created with ownership assigned to the database user
    specified in USER_DB_CONFIG["user"].
    """
    try:
        with psycopg.connect(**ADMIN_DB_CONFIG, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT 1 FROM information_schema.schemata WHERE schema_name = {};").format(
                        sql.Literal(SCHEMA_NAME)
                    )
                )
                if cur.fetchone():
                    log.info(f"Schema '{SCHEMA_NAME}' already exists")
                else:
                    cur.execute(
                        sql.SQL("CREATE SCHEMA {} AUTHORIZATION {};").format(
                            sql.Identifier(SCHEMA_NAME),
                            sql.Identifier(USER_DB_CONFIG["user"])
                        )
                    )
                    log.info(f"Schema '{SCHEMA_NAME}' created and owned by '{USER_DB_CONFIG['user']}'")
    except psycopg.OperationalError as e:
        log.error(f"Database {ADMIN_POSTGRES_CONFIG['dbname']} connection error: {e}")
        raise
    except psycopg.Error as e:
        log.error(f"Error creating schema '{SCHEMA_NAME}': {e}")
        raise
