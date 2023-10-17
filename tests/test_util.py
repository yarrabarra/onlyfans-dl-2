from pathlib import Path
from src import util

test_path = Path(__file__).parent


def test_cleanup_text():
    assert util.cleanup_text("\u2018\u2019*&lt;&gt;foo<br />") == "''<>foo\n"


def test_parse_pssh_from_mpd():
    """Ensures we get the expected pssh key from an MPD file"""
    expected = (
        "AAAAUnBzc2gAAAAA7e+LqXnWSs6j"
        "yCfc1R0h7QAAADIIARIQ9oxPpEFE"
        "g6bxVLarWwch8xoMaW5rYWVudHdv"
        "cmtzIgozMDIwMjMzMTUzKgJIRA=="
    )
    with open(test_path / "data/pssh.mpd", "r") as mpd_file:
        result = util.parse_pssh_from_mpd(mpd_file.read())
    assert result == expected


def test_get_session_config():
    util.get_session_config()
