import psycopg
from psycopg import sql
from logger import get_general_logger
from db.config import USER_DB_CONFIG, SCHEMA_NAME
from secret.client_settings import CLIENT

log = get_general_logger(__name__)


def insert_data(attempts_list):
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

                for att in attempts_list:
                    # Courses table
                    cur.execute(f"""
                        INSERT INTO {SCHEMA_NAME}.courses (name, client_id)
                        VALUES (%s, %s)
                        ON CONFLICT (name, client_id) DO NOTHING;
                    """, (att.course_name, client_id))

                    # Users table
                    cur.execute(f"""
                        INSERT INTO {SCHEMA_NAME}.users (external_id)
                        VALUES (%s)
                        ON CONFLICT (external_id) DO NOTHING;
                    """, (att.user_id, ))

                    # Targets table
                    cur.execute(f"""
                        INSERT INTO {SCHEMA_NAME}.targets (external_id)
                        VALUES (%s)
                        ON CONFLICT (external_id) DO NOTHING;
                    """, (att.target_id, ))

                    # Attempts table
                    cur.execute(f"""
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
                    """, (
                        att.created_at,
                        att.user_id,
                        att.course_name,
                        att.target_id,
                        att.attempt_type,
                        att.is_correct,
                        att.raw_oauth_consumer_key,
                        att.raw_lis_result_sourcedid,
                        att.raw_lis_outcome_service_url
                        ))
                log.info(f"{len(attempts_list)} attempts processed into the database. ")
        return True
    except psycopg.Error as e:
        log.error(f"Error inserting data: {e}")
        return False

