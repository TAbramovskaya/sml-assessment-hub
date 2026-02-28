import psycopg
from logger import get_general_logger
from db.config import USER_DB_CONFIG, SCHEMA_NAME
from secret.client_settings import CLIENT

log = get_general_logger(__name__)


def insert_data(attempts):
    """
    Inserts the data to the database specified in USER_DB_CONFIG["dbname"].
    See db/schema.sql for schema structure.
    """
    try:
        with psycopg.connect(**USER_DB_CONFIG, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Insert CLIENT in Clients table once
                cur.execute(f"""
                    INSERT INTO {SCHEMA_NAME}.clients (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                """, (CLIENT,))

                # get CLIENTs' id
                cur.execute(
                    f"SELECT id FROM {SCHEMA_NAME}.clients WHERE name = %s;",
                    (CLIENT,)
                )
                client_id = cur.fetchone()[0]

                # Collect unique courses, users and targets to insert them in one batch each.
                courses = {(att.course_name, client_id) for att in attempts}
                users = {(att.user_id, ) for att in attempts}
                targets = {(att.target_id, ) for att in attempts}

                # Insert all courses
                cur.executemany(
                    f"""
                        INSERT INTO {SCHEMA_NAME}.courses (name, client_id)
                        VALUES (%s, %s)
                        ON CONFLICT (name, client_id) DO NOTHING;
                    """,
                    list(courses)
                )

                # Insert all users
                cur.executemany(
                    f"""
                        INSERT INTO {SCHEMA_NAME}.users (external_id)
                        VALUES (%s)
                        ON CONFLICT (external_id) DO NOTHING;
                    """,
                    list(users)
                )

                # Insert all targets
                cur.executemany(
                    f"""
                        INSERT INTO {SCHEMA_NAME}.targets (external_id)
                        VALUES (%s)
                        ON CONFLICT (external_id) DO NOTHING;
                    """,
                    list(targets)
                )

                # Attempts table
                cur.executemany(f"""
                    INSERT INTO {SCHEMA_NAME}.attempts (
                        created_at, 
                        user_id, 
                        course_id, 
                        target_id,
                        attempt_type, 
                        is_correct,
                        raw_oauth_consumer_key,
                        raw_lis_result_sourcedid,
                        raw_lis_outcome_service_url
                        )
                    VALUES (
                        %s,
                        (SELECT id FROM {SCHEMA_NAME}.users WHERE external_id = %s),
                        (SELECT id FROM {SCHEMA_NAME}.courses WHERE name = %s),
                        (SELECT id FROM {SCHEMA_NAME}.targets WHERE external_id = %s),
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (user_id, created_at, raw_lis_result_sourcedid) DO NOTHING;
                """,
                    (
                        (att.created_at,
                        att.user_id,
                        att.course_name,
                        att.target_id,
                        att.attempt_type,
                        att.is_correct,
                        att.raw_oauth_consumer_key,
                        att.raw_lis_result_sourcedid,
                        att.raw_lis_outcome_service_url)
                        for att in attempts
                    )
                )

                log.info(f"Attempts successfully processed into the database")

    except psycopg.Error as e:
        log.error(f"Error inserting data: {e}")
        raise