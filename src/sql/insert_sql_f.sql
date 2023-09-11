INSERT
    OR IGNORE INTO downloads_failed (
        source,
        remote_file_size,
        remote_file_hash,
        local_file_size,
        local_file_hash,
        error,
        headers
    )
VALUES (?, ?, ?, ?, ?, ?, ?);