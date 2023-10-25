from src import ofdb


# Spin up a db
def test_to_str(tmp_path):
    db_path = tmp_path / "test.db"
    db = ofdb.OFDB(db_path=db_path)
    db.check_db("")
    db.close_db()
