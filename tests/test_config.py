"""Tests for config module."""

from pathlib import Path

from badminton_cli.config import clear_poi, get_poi, load_config, save_config, set_poi


def test_load_config_missing_file(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("badminton_cli.config.CONFIG_FILE", tmp_path / "nope.toml")
    assert load_config() == {}


def test_save_and_load_config(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "config.toml"
    monkeypatch.setattr("badminton_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("badminton_cli.config.CONFIG_FILE", cfg_file)

    save_config({"poi": "01-150083"})
    assert load_config() == {"poi": "01-150083"}


def test_set_and_get_poi(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "config.toml"
    monkeypatch.setattr("badminton_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("badminton_cli.config.CONFIG_FILE", cfg_file)

    assert get_poi() is None
    set_poi("01-150083")
    assert get_poi() == "01-150083"


def test_clear_poi(tmp_path: Path, monkeypatch):
    cfg_file = tmp_path / "config.toml"
    monkeypatch.setattr("badminton_cli.config.CONFIG_DIR", tmp_path)
    monkeypatch.setattr("badminton_cli.config.CONFIG_FILE", cfg_file)

    set_poi("01-150083")
    clear_poi()
    assert get_poi() is None
