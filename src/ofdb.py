import sqlite3
import os

from pathlib import Path
from loguru import logger as log

script_dir = Path(__file__).absolute().parent


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def load_sql(name: str):
    with open(script_dir / f"sql/{name}.sql") as sqlFile:
        return sqlFile.read()


class OFDB:
    db_path: str

    def __init__(self, db_path="data_ofd.db"):
        self.db_path = db_path
        log.info("Opening DB connection...")
        self.create_db_if_not_exists()
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = dict_factory
        log.info("DB connection opened.")

    def create_db_if_not_exists(self):
        if not os.path.exists(self.db_path):
            dlc_table_sql = load_sql("dlc_table")
            dlc_trigger_sql = load_sql("dlc_trigger")
            dlf_table_sql = load_sql("dlf_table")
            dlf_trigger_sql = load_sql("dlf_trigger")

            db = sqlite3.connect(self.db_path)
            cur = db.cursor()
            cur.execute(dlc_table_sql)
            cur.execute(dlc_trigger_sql)
            cur.execute(dlf_table_sql)
            cur.execute(dlf_trigger_sql)

            db.commit()
            cur.close()
            db.close()

    def check_db(self, source):
        cur_ck = self.db.cursor()

        check_cleared_sql = "SELECT count(dlc_id) AS dlc_count FROM downloads_cleared WHERE source = ?;"
        check_failed_sql = "SELECT count(dlf_id) AS dlf_count FROM downloads_failed WHERE source = ? AND status = 'a';"

        res_c = cur_ck.execute(check_cleared_sql, (source,)).fetchone()
        res_f = cur_ck.execute(check_failed_sql, (source,)).fetchone()

        count_c = res_c["dlc_count"]
        count_f = res_f["dlf_count"]
        total = count_c + count_f

        if total == 0:
            return False

        elif total == 1:
            return True
        else:
            err = f"Error in DB rows for source: {source} | Rows found: {total}"
            log.critical(err)
            raise (RuntimeError(err))

    def close_db(self):
        log.info("Closing DB...")
        self.db.close()
        log.info("DB closed.")

    def insert_into_downloads_cleared(
        self,
        source,
        remote_file_size,
        remote_file_hash,
        local_file_size,
        local_file_hash,
    ):
        cur_c = self.db.cursor()

        insert_sql_c = load_sql("insert_sql_c")

        cur_c.execute(
            insert_sql_c,
            (
                source,
                remote_file_size,
                remote_file_hash,
                local_file_size,
                local_file_hash,
            ),
        )
        self.db.commit()

        cur_c.close()

    def insert_into_downloads_failed(
        self,
        source,
        remote_file_size,
        remote_file_hash,
        local_file_size,
        local_file_hash,
        error,
        headers,
    ):
        cur_f = self.db.cursor()

        insert_sql_f = load_sql("insert_sql_f")

        cur_f.execute(
            insert_sql_f,
            (
                source,
                remote_file_size,
                remote_file_hash,
                local_file_size,
                local_file_hash,
                error,
                headers,
            ),
        )
        self.db.commit()

        cur_f.close()
