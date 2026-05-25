CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS articulations;
DROP TABLE IF EXISTS receiving_requirements;
DROP TABLE IF EXISTS courses;

CREATE TABLE IF NOT EXISTS institutions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    is_community_college BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS academic_years (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL
);

CREATE TABLE courses (
    id BIGINT PRIMARY KEY,
    institution_id INTEGER NOT NULL REFERENCES institutions(id),
    prefix TEXT,
    course_number TEXT,
    course_key TEXT,
    title TEXT,
    department TEXT,
    min_units NUMERIC,
    max_units NUMERIC
);

CREATE TABLE receiving_requirements (
    id TEXT PRIMARY KEY,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id),
    receiving_institution_id INTEGER NOT NULL REFERENCES institutions(id),
    requirement_type TEXT NOT NULL,
    display_key TEXT,
    title TEXT,
    requirement_json JSONB NOT NULL
);

CREATE TABLE articulations (
    id BIGSERIAL PRIMARY KEY,
    academic_year_id INTEGER NOT NULL REFERENCES academic_years(id),
    receiving_institution_id INTEGER NOT NULL REFERENCES institutions(id),
    sending_institution_id INTEGER NOT NULL REFERENCES institutions(id),
    receiving_requirement_id TEXT NOT NULL REFERENCES receiving_requirements(id),
    group_name TEXT,
    source_file TEXT NOT NULL,
    receiving_json JSONB NOT NULL,
    sending_json JSONB NOT NULL,
    UNIQUE (
        academic_year_id,
        receiving_institution_id,
        sending_institution_id,
        receiving_requirement_id,
        group_name,
        source_file
    )
);

CREATE INDEX courses_institution_prefix_number_idx
ON courses (institution_id, prefix, course_number);

CREATE INDEX courses_course_key_idx
ON courses (course_key);

CREATE INDEX courses_course_key_trgm_idx
ON courses USING gin (course_key gin_trgm_ops);

CREATE INDEX courses_title_trgm_idx
ON courses USING gin (title gin_trgm_ops);

CREATE INDEX receiving_requirements_display_key_idx
ON receiving_requirements (display_key);

CREATE INDEX receiving_requirements_display_key_trgm_idx
ON receiving_requirements USING gin (display_key gin_trgm_ops);

CREATE INDEX receiving_requirements_title_trgm_idx
ON receiving_requirements USING gin (title gin_trgm_ops);

CREATE INDEX institutions_name_trgm_idx
ON institutions USING gin (name gin_trgm_ops);

CREATE INDEX articulations_receiving_requirement_idx
ON articulations (receiving_requirement_id);

CREATE INDEX articulations_sending_institution_idx
ON articulations (sending_institution_id);

CREATE INDEX articulations_academic_year_idx
ON articulations (academic_year_id);

CREATE INDEX articulations_sending_json_gin_idx
ON articulations USING gin (sending_json);
