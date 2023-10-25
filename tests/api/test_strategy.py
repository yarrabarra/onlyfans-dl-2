import requests_mock
import json
import click

from src.api import strategy


def test_signed_requests_builds(tmp_path):
    config_path = tmp_path / "test.json"
    ctx = click.Context(click.Command("cmd"))
    ctx.params["session_vars_path"] = config_path
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

    with ctx:
        strat = strategy.SignedRequestsStrategy()
        strat._create_signed_headers("http://localhost", {"foo": "bar"})
