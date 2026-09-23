"""
Por que essa abordagem na camada Bronze?
Preservação do Dado Bruto (Raw Fidelity): A camada Bronze serve como 
réplica exata do dado de origem. Nenhuma limpeza, alteração de nome de coluna ou 
conversão de tipo deve acontecer aqui.

Eficiência Colunar: Converter CSV para Parquet reduz drasticamente o tempo 
de leitura e o uso de memória para as camadas seguintes (Silver/Gold), aproveitando 
a compressão nativa Snappy/ZSTD.

Leitura Genérica/Parametrizada: Uma função utilitária que recebe o nome do dataset 
torna o código limpo, reaproveitável e fácil de testar.   
  
"""

"""
Módulo de Ingestão - Camada Bronze
----------------------------------
Responsável por converter os arquivos brutos CSV em formato Parquet.
Garante a fidelidade dos dados originais (Raw Fidelity) e otimização colunar.
"""

from pathlib import Path
import polars as pl

# Importação dos caminhos mapeados dinamicamente no config.py
from src.config import BRONZE_DIR, RAW_DIR


def convert_csv_to_parquet(file_name: str) -> Path:
    """
    Lê um arquivo CSV da pasta raw/ e salva em formato colunar Parquet na pasta bronze/.

    Parâmetros:
        file_name (str): Nome base do arquivo sem a extensão (ex: 'contracts').

    Retorno:
        Path: Caminho absoluto do arquivo Parquet gerado em data/bronze/.

    Exceções:
        FileNotFoundError: Lançado caso o CSV de origem não seja encontrado.
    """
    # 1. Montagem dinâmica dos caminhos de origem (CSV) e destino (Parquet)
    raw_path = RAW_DIR / f"{file_name}.csv"
    bronze_path = BRONZE_DIR / f"{file_name}.parquet"

    # 2. Defesa: Verifica se o arquivo bruto realmente existe antes de tentar a leitura
    if not raw_path.exists():
        raise FileNotFoundError(f"Arquivo bruto não encontrado: {raw_path}")

    # 3. Leitura do CSV bruto usando Polars (alta performance de I/O)
    # Nota: Nenhuma transformação ou filtro é aplicado aqui para manter a réplica idêntica
    df = pl.read_csv(raw_path)

    # 4. Escrita do DataFrame no formato Parquet (compactado e otimizado para consultas)
    df.write_parquet(bronze_path)

    # 5. Retorna o caminho do arquivo gerado para controle ou validação dos testes
    return bronze_path


def run_ingestion() -> list[Path]:
    """
    Orquestrador do processo de ingestão da camada Bronze.
    Executa a conversão para todos os datasets principais do projeto.

    Retorno:
        list[Path]: Lista de caminhos dos arquivos .parquet criados na pasta bronze/.
    """
    # Lista com os nomes dos datasets esperados na pasta data/raw/
    datasets = ["contracts", "market_prices", "counterparties_limits"]

    # Executa a função de conversão para cada dataset da lista via List Comprehension
    return [convert_csv_to_parquet(ds) for ds in datasets]