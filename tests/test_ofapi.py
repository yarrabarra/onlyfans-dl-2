import click
from src import ofapi
from freezegun import freeze_time


# test dest
def test_to_str():
    assert ofapi.to_str("0.1") == "0.1"
    assert ofapi.to_str(0.5) == "0.500000"
    assert ofapi.to_str(1) == "1"


@freeze_time("2023-01-23")
def test_get_max_days_offset():
    # param = click.Option(max_post_days=0)?
    ctx = click.Context(click.Command("cmd"))
    ctx.params["max_post_days"] = 14
    with ctx:
        assert ofapi.get_max_days_offset() >= 1673222400.0
