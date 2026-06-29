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


-----------------------------------------------------------
-- Supports ordered-by-time scans per API name (timeline + downsampling),
-- and range filtering on called_at.
CREATE INDEX IF NOT EXISTS idx_api_history_api_called
    ON api_history (api_name, called_at);
