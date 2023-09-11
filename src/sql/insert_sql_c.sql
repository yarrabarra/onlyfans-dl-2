INSERT
    OR IGNORE INTO downloads_cleared (
        source,
        remote_file_size,
        remote_file_hash,
        local_file_size,
        local_file_hash
    )
VALUES (?, ?, ?, ?, ?);