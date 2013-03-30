CREATE TABLE battles (
    id SERIAL,
    user1 INTEGER,
    user2 INTEGER,
    started_time TIMESTAMP DEFAULT NOW(),
    winner_userid INTEGER DEFAULT NULL
);

CREATE TABLE battle_answers (
    id SERIAL,
    battle_id INTEGER,
    points INTEGER,
    user_id INTEGER,
    time TIMESTAMP DEFAULT NOW()
);

CREATE TABLE battle_scores (
    id SERIAL,
    user_id INTEGER,
    battle_id INTEGER,
    score INTEGER,
    time TIMESTAMP DEFAULT NOW()
);
