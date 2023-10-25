import click
import json

from pathlib import Path

import pytest
from src import util

test_path = Path(__file__).parent


def test_cleanup_text():
    result = util.cleanup_text("\u2018\u2019*&lt;&gt;foo<br />")
    assert result == "''<>foo\n"


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


def test_get_session_config_loads(tmp_path):
    config_path = tmp_path / "test.json"
    ctx = click.Context(click.Command("cmd"))
    ctx.params["session_vars_path"] = config_path

    with ctx:
        # Validate no file
        with pytest.raises(IOError):
            util.get_session_config()

        with open(test_path / "../session_vars.sample.json") as sample_file:
            sample_vars = json.load(sample_file)

        # Validate sample file
        with open(config_path, "w") as tmp_file:
            json.dump(sample_vars, tmp_file)
        with pytest.raises(ValueError):
            util.get_session_config()

        # Validate values
        with open(config_path, "w") as tmp_file:
            json.dump(
                {
                    "USER_ID": "a",
                    "USER_AGENT": "b",
                    "SESS_COOKIE": "c",
                    "X_BC": "d",
                },
                tmp_file,
            )

        config = util.get_session_config()
        assert config["USER_ID"] == "a"
