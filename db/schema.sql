-- Users table
CREATE TABLE IF NOT EXISTS <schema_name>.users (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,
    alias TEXT
);

-- Targets table
CREATE TABLE IF NOT EXISTS <schema_name>.targets (
    id BIGSERIAL PRIMARY KEY,
    external_id TEXT NOT NULL UNIQUE,
    alias TEXT
);

-- Courses table
CREATE TABLE IF NOT EXISTS <schema_name>.courses (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    alias TEXT
);

-- Attempts table
CREATE TABLE IF NOT EXISTS <schema_name>.attempts (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,

    user_id BIGINT NOT NULL REFERENCES <schema_name>.users(id),
    course_id BIGINT REFERENCES <schema_name>.courses(id),
    target_id BIGINT REFERENCES <schema_name>.targets(id),

    attempt_type TEXT NOT NULL,
    is_correct SMALLINT,

    raw_oauth_consumer_key TEXT,
    raw_lis_result_sourcedid TEXT NOT NULL,
    raw_lis_outcome_service_url TEXT,

    UNIQUE (user_id, created_at, raw_lis_result_sourcedid)
);