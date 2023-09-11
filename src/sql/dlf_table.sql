CREATE TABLE IF NOT EXISTS downloads_failed (
    dlf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR (255),
    remote_file_size INTEGER,
    remote_file_hash VARCHAR (255),
    local_file_size INTEGER,
    local_file_hash VARCHAR (255),
    error VARCHAR (255),
    headers TEXT,
    status CHAR (1) DEFAULT a,
    added_ts DATETIME (255) DEFAULT (datetime('now', 'localtime')) NOT NULL,
    last_updated_ts DATETIME DEFAULT (datetime('now', 'localtime')) NOT NULL
);