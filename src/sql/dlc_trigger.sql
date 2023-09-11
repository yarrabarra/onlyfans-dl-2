CREATE TRIGGER IF NOT EXISTS downloads_cleared_update_timestamp
AFTER
UPDATE ON downloads_cleared FOR EACH ROW
    WHEN new.last_updated_ts <= old.last_updated_ts BEGIN
UPDATE downloads_cleared
SET last_updated_ts = datetime('now', 'localtime')
WHERE dlc_id = old.dlc_id;
END;