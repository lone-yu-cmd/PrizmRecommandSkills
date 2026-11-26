import json
import os

CONFIG_PATH = os.path.expanduser("~/.config/syncer/config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {
        "endpoint": data["endpoint"],
        "targets": data["targets"],
        "token": data.get("token", ""),
    }
