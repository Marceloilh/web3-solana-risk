"""
Portabilidade Universal: Usar pathlib.Path(__file__).resolve().parent.parent 
garante que o projeto rode sem alterações em Windows, Linux ou macOS, 
independente do diretório de onde o script for chamado.

"""

from pathlib import Path

# 1. Diretório Raiz do Projeto (src/config.py -> parent -> parent)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Diretórios de Dados (Data Lake Local)
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"


def ensure_directories_exist() -> None:
    """Garante que todas as pastas de dados existam no sistema de arquivos."""
    for path in [RAW_DIR, BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
        path.mkdir(parents=True, exist_ok=True)