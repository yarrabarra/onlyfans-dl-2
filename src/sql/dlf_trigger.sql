CREATE TRIGGER IF NOT EXISTS downloads_failed_update_timestamp
AFTER
UPDATE ON downloads_failed FOR EACH ROW
    WHEN new.last_updated_ts <= old.last_updated_ts BEGIN
UPDATE downloads_failed
SET last_updated_ts = datetime('now', 'localtime')
WHERE dlf_id = old.dlf_id;
END;