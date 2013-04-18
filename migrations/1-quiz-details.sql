ALTER TABLE quiz ADD COLUMN actual_type VARCHAR;
ALTER TABLE quiz ADD COLUMN difficulty VARCHAR;

CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    score_time TIMESTAMP DEFAULT NOW(),
    user_id INTEGER,
    quiz_id INTEGER,
    quiz_type VARCHAR,
    difficulty VARCHAR,
    score INTEGER
);