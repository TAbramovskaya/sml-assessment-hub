import psycopg
from psycopg import sql
from logger import get_general_logger
from db.config import ADMIN_POSTGRES_CONFIG, ADMIN_DB_CONFIG, USER_DB_CONFIG, SCHEMA_NAME

log = get_general_logger(__name__)


def db_create_if_not_exist():
    with psycopg.connect(**ADMIN_POSTGRES_CONFIG, autocommit=True) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT 1 FROM pg_database WHERE datname = {};").format(
                        sql.Literal(USER_DB_CONFIG['dbname'])
                    )
                )
                if cur.fetchone():
                    print("Database {} already exists".format(USER_DB_CONFIG['dbname']))
                    return False

                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(USER_DB_CONFIG['dbname'])
                    )
                )
                log.info(f"Database {USER_DB_CONFIG['dbname']} created")
                return True

        except psycopg.OperationalError as e:
            log.error(f"Database {ADMIN_POSTGRES_CONFIG['dbname']} connection error: {e}")
            raise


def user_create_if_not_exist():
    try:
        with psycopg.connect(**ADMIN_POSTGRES_CONFIG, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT 1 FROM pg_roles WHERE rolname = {};").format(
                        sql.Literal(USER_DB_CONFIG['user'])
                    )
                )
                if cur.fetchone():
                    print(f"User {USER_DB_CONFIG['user']} already exists")
                    return False

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
    try:
        with psycopg.connect(**ADMIN_DB_CONFIG, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql.SQL("SELECT 1 FROM information_schema.schemata WHERE schema_name = {};").format(
                        sql.Literal(SCHEMA_NAME)
                    )
                )
                if cur.fetchone():
                    print(f"Schema '{SCHEMA_NAME}' already exists")
                    return False

                cur.execute(
                    sql.SQL("CREATE SCHEMA {} AUTHORIZATION {};").format(
                        sql.Identifier(SCHEMA_NAME),
                        sql.Identifier(USER_DB_CONFIG["user"])
                    )
                )

                log.info(f"Schema '{SCHEMA_NAME}' created and owned by '{USER_DB_CONFIG['user']}'")
                return True

    except psycopg.Error as e:
        log.error(f"Error creating schema '{SCHEMA_NAME}': {e}")
        raise

