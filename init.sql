-- init.sql
-- Runs once when the Postgres container starts for the first time.
-- Creates the tasks table and seeds 3 example rows.

CREATE TABLE IF NOT EXISTS tasks (
    id    SERIAL PRIMARY KEY,
    title TEXT    NOT NULL,
    done  BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, done)
SELECT title, done FROM (VALUES
    ('Buy groceries',      FALSE),
    ('Read FastAPI docs',  TRUE),
    ('Push code to GitHub',FALSE)
) AS seed(title, done)
WHERE NOT EXISTS (SELECT 1 FROM tasks LIMIT 1);
