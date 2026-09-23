"""
Testes Unitários - Schemas e Validação Pydantic (src/engine/schemas.py)
------------------------------------------------------------------------
Valida os contratos de dados para garantir integridade antes das transformações Silver.
"""

from datetime import date
import pytest
from pydantic import ValidationError

from src.engine.schemas import (
    ContractSchema,
    CounterpartyLimitSchema,
    MarketPriceSchema,
)


# ==========================================
# TESTES: ContractSchema
# ==========================================

def test_contract_schema_valid():
    """Garante que um contrato perfeitamente preenchido é aceito."""
    valid_data = {
        "contract_id": "CT-1001",
        "counterparty_id": "CP-ALPHA",
        "submarket": "SE",
        "type": "BUY",
        "volume_mwm": 12.5,
        "strike_price_brl": 280.50,
        "start_date": date(2026, 10, 1),
        "end_date": date(2026, 10, 31),
    }
    contract = ContractSchema(**valid_data)
    assert contract.contract_id == "CT-1001"
    assert contract.submarket == "SE"
    assert contract.volume_mwm == 12.5


@pytest.mark.parametrize(
    "invalid_field, invalid_value",
    [
        ("submarket", "XINA"),          # Submercado inexistente (deve ser SE, S, NE ou N)
        ("type", "HOLD"),               # Operação inválida (deve ser BUY ou SELL)
        ("volume_mwm", 0.0),            # Volume precisa ser estritamente positivo (> 0)
        ("volume_mwm", -10.0),          # Volume negativo
        ("strike_price_brl", -50.0),     # Preço strike negativo
        ("contract_id", ""),            # ID vazio
    ],
)
def test_contract_schema_invalid_inputs(invalid_field, invalid_value):
    """Garante que entradas fora da regra de negócio disparam ValidationError."""
    valid_data = {
        "contract_id": "CT-1001",
        "counterparty_id": "CP-ALPHA",
        "submarket": "SE",
        "type": "BUY",
        "volume_mwm": 12.5,
        "strike_price_brl": 280.50,
        "start_date": date(2026, 10, 1),
        "end_date": date(2026, 10, 31),
    }
    valid_data[invalid_field] = invalid_value

    with pytest.raises(ValidationError):
        ContractSchema(**valid_data)


# ==========================================
# TESTES: MarketPriceSchema
# ==========================================

def test_market_price_schema_valid():
    """Valida o schema de preço de mercado para meses no formato YYYY-MM."""
    valid_data = {
        "submarket": "S",
        "reference_month": "2026-10",
        "price_brl": 310.00,
    }
    price = MarketPriceSchema(**valid_data)
    assert price.submarket == "S"
    assert price.reference_month == "2026-10"


@pytest.mark.parametrize(
    "invalid_month, invalid_price",
    [
        ("2026/10", 200.0),    # Formato de data incorreto (deve ser YYYY-MM)
        ("2026-1", 200.0),     # Mês sem zero à esquerda
        ("2026-10", -15.0),    # Preço de mercado estritamente positivo (> 0)
    ],
)
def test_market_price_schema_invalid(invalid_month, invalid_price):
    """Garante rejeição de formatos de mês inválidos ou preços não positivos."""
    with pytest.raises(ValidationError):
        MarketPriceSchema(
            submarket="SE",
            reference_month=invalid_month,
            price_brl=invalid_price,
        )


# ==========================================
# TESTES: CounterpartyLimitSchema
# ==========================================

def test_counterparty_limit_schema_valid():
    """Valida o limite de crédito aceitando valores >= 0."""
    valid_data = {
        "counterparty_id": "CP-BETA",
        "credit_limit_brl": 500000.00,
    }
    limit = CounterpartyLimitSchema(**valid_data)
    assert limit.credit_limit_brl == 500000.00


def test_counterparty_limit_schema_negative_limit():
    """Garante que limites de crédito não podem ser negativos."""
    with pytest.raises(ValidationError):
        CounterpartyLimitSchema(
            counterparty_id="CP-BETA",
            credit_limit_brl=-1000.00,
        )