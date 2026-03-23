-----------------------------------------------------------
DROP TABLE IF EXISTS api_history CASCADE;


-----------------------------------------------------------
CREATE TABLE api_history (
    id          SERIAL PRIMARY KEY,
    api_name    VARCHAR(64)  NOT NULL,
    success     BOOLEAN      NOT NULL,
    duration_ms INTEGER      NOT NULL DEFAULT 0,
    message     TEXT         NOT NULL DEFAULT '',
    called_at   TIMESTAMP    NOT NULL DEFAULT now()
);
