"""Configuration management for badminton-cli."""

import tomllib
from pathlib import Path

from platformdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir("badminton-cli"))
CONFIG_FILE = CONFIG_DIR / "config.toml"


def get_config_path() -> Path:
    return CONFIG_FILE


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in config.items():
        if isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        elif isinstance(value, bool):
            lines.append(f"{key} = {'true' if value else 'false'}")
        elif isinstance(value, int | float):
            lines.append(f"{key} = {value}")
    CONFIG_FILE.write_text("\n".join(lines) + "\n")


def get_poi() -> str | None:
    config = load_config()
    return config.get("poi")


def set_poi(player_id: str) -> None:
    config = load_config()
    config["poi"] = player_id
    save_config(config)


def clear_poi() -> None:
    config = load_config()
    config.pop("poi", None)
    save_config(config)
