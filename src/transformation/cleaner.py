"""
 Por que essa conversão importa?No mercado livre de energia elétric da CCEE, 
 o volume comercializado em contratos é expressado em MWm (potência constante no período).
 Porém, a liquidação financeira (Mark-to-Market) é calculada sobre o volume total em MWh.
 
 Fórmula: Volume (MWh) = Volume (MWm) X Horas do Mês
 
 Desafio de Engenharia: Meses têm durações diferentes (720h para meses de 30 dias, 744h para meses de 31 dias, 
 672h ou 696h em anos bissextos para fevereiro). O código precisa calcular a quantidade exata de horas
 do mês vigentes no contrato com precisão cirúrgica.   
       
"""
"""
Módulo de Limpeza e Tratamento - Camada Silver
----------------------------------------------
Aplica a conversão do volume de MWm para MWh com base no número exato de horas do mês
e escreve os dados limpos em data/silver/.
"""

import calendar
from datetime import date
from pathlib import Path
import polars as pl

from src.config import BRONZE_DIR, SILVER_DIR


def get_hours_in_month(year: int, month: int) -> int:
    """Retorna o número total de horas em um determinado mês/ano."""
    _, num_days = calendar.monthrange(year, month)
    return num_days * 24


def clean_contracts() -> Path:
    """
    Lê os contratos brutos da Bronze, converte datas, calcula a quantidade total
    de horas do mês do suprimento e converte Volume (MWm) -> Volume (MWh).
    """
    bronze_path = BRONZE_DIR / "contracts.parquet"
    silver_path = SILVER_DIR / "contracts.parquet"

    if not bronze_path.exists():
        raise FileNotFoundError(f"Arquivo Bronze não encontrado: {bronze_path}")

    df = pl.read_parquet(bronze_path)

    # Garante parsing das datas
    df = df.with_columns([
        pl.col("start_date").str.to_date().alias("start_date"),
        pl.col("end_date").str.to_date().alias("end_date"),
    ])

    # Extrai ano e mês do início do suprimento para cálculo de horas
    df = df.with_columns([
        pl.col("start_date").dt.year().alias("year"),
        pl.col("start_date").dt.month().alias("month"),
    ])

    # Aplica o cálculo exato de horas usando a função get_hours_in_month
    hours_expr = pl.struct(["year", "month"]).map_elements(
        lambda row: get_hours_in_month(row["year"], row["month"]),
        return_dtype=pl.Int64
    )

    df = df.with_columns([
        hours_expr.alias("month_hours"),
    ])

    # Aplica a Regra do Mercado de Energia: MWh = MWm * Horas do Mês
    df = df.with_columns([
        (pl.col("volume_mwm") * pl.col("month_hours")).alias("volume_mwh")
    ])

    # Escreve o resultado transformado na camada Silver
    df.write_parquet(silver_path)
    return silver_path