from pathlib import Path
import pytest

from src.config import (
    BASE_DIR,
    BRONZE_DIR,
    DATA_DIR,
    GOLD_DIR,
    RAW_DIR,
    SILVER_DIR,
    ensure_directories_exist,
)


def test_config_paths_are_path_instances():
    """Garante que todos os caminhos exportados são objetos Path do pathlib."""
    paths = [BASE_DIR, DATA_DIR, RAW_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR]
    for p in paths:
        assert isinstance(p, Path)


def test_base_dir_structure():
    """Verifica se a pasta 'data' está imediatamente abaixo do 'BASE_DIR'."""
    assert DATA_DIR == BASE_DIR / "data"
    assert RAW_DIR == DATA_DIR / "raw"
    assert BRONZE_DIR == DATA_DIR / "bronze"
    assert SILVER_DIR == DATA_DIR / "silver"
    assert GOLD_DIR == DATA_DIR / "gold"


def test_ensure_directories_exist():
    """Garante que a função cria fisicamente os diretórios no disco."""
    ensure_directories_exist()

    assert RAW_DIR.exists() and RAW_DIR.is_dir()
    assert BRONZE_DIR.exists() and BRONZE_DIR.is_dir()
    assert SILVER_DIR.exists() and SILVER_DIR.is_dir()
    assert GOLD_DIR.exists() and GOLD_DIR.is_dir()