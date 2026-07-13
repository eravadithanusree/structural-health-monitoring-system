-- Structural Health Monitoring System schema
-- SQLite

CREATE TABLE IF NOT EXISTS readings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    structure_id  TEXT    NOT NULL DEFAULT 'default',
    vibration     REAL    NOT NULL,
    strain        REAL    NOT NULL,
    temperature   REAL    NOT NULL,
    status        TEXT    NOT NULL,               -- 'Healthy' | 'Damaged'
    confidence    REAL,                            -- model confidence 0-1
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_readings_created_at ON readings (created_at);
CREATE INDEX IF NOT EXISTS idx_readings_structure ON readings (structure_id);

CREATE TABLE IF NOT EXISTS structures (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    type          TEXT NOT NULL,                   -- Bridge | Building | Dam | Tower
    location      TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO structures (id, name, type, location)
VALUES ('default', 'Riverside Bridge', 'Bridge', 'Sector 4');
