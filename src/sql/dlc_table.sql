CREATE TABLE IF NOT EXISTS downloads_cleared (
    dlc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR (255) UNIQUE,
    remote_file_size INTEGER,
    remote_file_hash VARCHAR (255),
    local_file_size INTEGER,
    local_file_hash VARCHAR (255),
    added_ts DATETIME (255) DEFAULT (datetime('now', 'localtime')) NOT NULL,
    last_updated_ts DATETIME DEFAULT (datetime('now', 'localtime')) NOT NULL
);