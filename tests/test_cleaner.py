"""
Testes Unitários - Tratamento e Regra de MWh (src/transformation/cleaner.py)
-----------------------------------------------------------------------------
Valida a precisão do cálculo de horas por mês e a conversão de MWm para MWh.
"""

from pathlib import Path
import polars as pl
import pytest

from src.transformation.cleaner import clean_contracts, get_hours_in_month


# ==========================================
# TESTES: get_hours_in_month
# ==========================================

@pytest.mark.parametrize(
    "year, month, expected_hours",
    [
        (2026, 10, 744),  # Outubro (31 dias * 24h = 744h)
        (2026, 11, 720),  # Novembro (30 dias * 24h = 720h)
        (2026, 2, 672),   # Fevereiro Comum (28 dias * 24h = 672h)
        (2024, 2, 696),   # Fevereiro Bissexto (29 dias * 24h = 696h)
    ],
)
def test_get_hours_in_month_precision(year, month, expected_hours):
    """Garante a contagem exata de horas para meses normais e bissextos."""
    assert get_hours_in_month(year, month) == expected_hours


# ==========================================
# TESTES: clean_contracts (Camada Silver)
# ==========================================

def test_clean_contracts_mwh_conversion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Testa a conversão completa do pipeline Silver:
    Lê o Bronze, calcula o mês/horas e gera o volume em MWh.
    """
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"
    bronze_dir.mkdir()
    silver_dir.mkdir()

    monkeypatch.setattr("src.transformation.cleaner.BRONZE_DIR", bronze_dir)
    monkeypatch.setattr("src.transformation.cleaner.SILVER_DIR", silver_dir)

    # 1. Cria um Parquet sintético simulando a camada Bronze
    sample_data = pl.DataFrame({
        "contract_id": ["CT-01", "CT-02"],
        "counterparty_id": ["CP-A", "CP-B"],
        "submarket": ["SE", "S"],
        "type": ["BUY", "SELL"],
        "volume_mwm": [10.0, 5.0],  # 10 MWm e 5 MWm
        "strike_price_brl": [250.0, 300.0],
        "start_date": ["2026-10-01", "2026-11-01"],  # Outubro (744h) e Novembro (720h)
        "end_date": ["2026-10-31", "2026-11-30"],
    })

    sample_data.write_parquet(bronze_dir / "contracts.parquet")

    # 2. Executa a limpeza
    silver_path = clean_contracts()

    # 3. Validações
    assert silver_path.exists()

    df_silver = pl.read_parquet(silver_path)

    # CT-01 (Outubro): 10 MWm * 744h = 7440 MWh
    # CT-02 (Novembro): 5 MWm * 720h = 3600 MWh
    expected_mwh = [7440.0, 3600.0]
    expected_hours = [744, 720]

    assert df_silver["month_hours"].to_list() == expected_hours
    assert df_silver["volume_mwh"].to_list() == expected_mwh
    assert df_silver["start_date"].dtype == pl.Date


def test_clean_contracts_missing_bronze_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Garante exceção caso o arquivo de contratos na Bronze não exista."""
    monkeypatch.setattr("src.transformation.cleaner.BRONZE_DIR", tmp_path)

    with pytest.raises(FileNotFoundError, match="Arquivo Bronze não encontrado"):
        clean_contracts()