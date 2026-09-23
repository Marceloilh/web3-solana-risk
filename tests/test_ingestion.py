"""
Testes Unitários - Ingestão Bronze (src/ingestion/loader.py)
------------------------------------------------------------
Testa a conversão de CSV para Parquet e a orquestração do pipeline Bronze.
"""

from pathlib import Path
import polars as pl
import pytest

from src.ingestion.loader import convert_csv_to_parquet, run_ingestion


def test_convert_csv_to_parquet_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Testa se a conversão de CSV para Parquet mantém o mesmo número de linhas
    e colunas sem perdas de dados.
    """
    # 1. Configura diretórios temporários para isolar o teste
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    raw_dir.mkdir()
    bronze_dir.mkdir()

    # Redireciona as constantes RAW_DIR e BRONZE_DIR para os caminhos temporários
    monkeypatch.setattr("src.ingestion.loader.RAW_DIR", raw_dir)
    monkeypatch.setattr("src.ingestion.loader.BRONZE_DIR", bronze_dir)

    # 2. Cria um arquivo CSV fictício na pasta raw temporária
    csv_path = raw_dir / "sample_data.csv"
    csv_content = "id,name,value\n1,Alpha,100.5\n2,Beta,200.0\n3,Gamma,300.75\n"
    csv_path.write_text(csv_content, encoding="utf-8")

    # 3. Executa a conversão
    parquet_path = convert_csv_to_parquet("sample_data")

    # 4. Asserções
    assert parquet_path.exists()
    assert parquet_path.suffix == ".parquet"

    # Carrega ambos os arquivos para garantir integridade dos dados
    df_original = pl.read_csv(csv_path)
    df_converted = pl.read_parquet(parquet_path)

    assert df_converted.shape == df_original.shape
    assert df_converted.columns == df_original.columns


def test_convert_csv_to_parquet_file_not_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Garante que um FileNotFoundError é lançado se o CSV de origem não existir."""
    monkeypatch.setattr("src.ingestion.loader.RAW_DIR", tmp_path)

    with pytest.raises(FileNotFoundError, match="Arquivo bruto não encontrado"):
        convert_csv_to_parquet("inexistent_file")


def test_run_ingestion_executes_all_datasets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Testa a execução do orquestrador run_ingestion para os três datasets previstos."""
    raw_dir = tmp_path / "raw"
    bronze_dir = tmp_path / "bronze"
    raw_dir.mkdir()
    bronze_dir.mkdir()

    monkeypatch.setattr("src.ingestion.loader.RAW_DIR", raw_dir)
    monkeypatch.setattr("src.ingestion.loader.BRONZE_DIR", bronze_dir)

    # Cria os 3 arquivos brutos simulados esperados pelo orquestrador
    datasets = ["contracts", "market_prices", "counterparties_limits"]
    for ds in datasets:
        (raw_dir / f"{ds}.csv").write_text("col1,col2\n1,a\n2,b\n", encoding="utf-8")

    # Executa a ingestão completa
    generated_files = run_ingestion()

    # Valida que todos os 3 arquivos .parquet foram gerados
    assert len(generated_files) == 3
    for file_path in generated_files:
        assert file_path.exists()
        assert file_path.suffix == ".parquet"