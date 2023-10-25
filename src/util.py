import os
import click
import json
import xmltodict
from models.mpd import BaseMPD


def cleanup_text(text):
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "*": "",
        "&lt;": "<",
        "&gt;": ">",
        "<br />": "\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


@click.pass_context
def get_session_config(ctx):
    session_vars_path = ctx.params["session_vars_path"]
    if not os.path.exists(session_vars_path):
        raise IOError(f"Missing {session_vars_path}, see README.md for configuration")
    with open(session_vars_path, "r") as jsonFile:
        config = json.load(jsonFile)
        for var in ("USER_ID", "USER_AGENT", "SESS_COOKIE", "X_BC"):
            if len(config.get(var, "")) == 0:
                raise ValueError(f"Config key {var} is missing or empty")
    return config


def parse_pssh_from_mpd(mpd_text):
    mpd = BaseMPD.model_validate(xmltodict.parse(mpd_text))
    for period in mpd.MPD.Period:
        for ad_set in period.AdaptationSet:
            if not ad_set.mimeType == "video/mp4":
                continue
            for item in ad_set.ContentProtection:
                if item.schemeIdUri.lower() == "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed":
                    return item.cenc_pssh
    return None
