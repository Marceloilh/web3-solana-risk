"""
Por que criar contratos com Pydantic?
Defesa em Profundidade: Impede que dados corrompidos ou inconsistentes 
(como preços negativos ou submercados inexistentes) avancem para os motores
de cálculo financeiro (Risk Engine).

Documentação Viva: O schema documenta explicitamente o que a pipeline espera 
receber e quais são as restrições de negócio.

Erros Explícitos: Lança exceções detalhadas indicando exatamente qual coluna e 
linha violaram a regra de integridade.      
    
"""
"""
Módulo de Schemas e Contratos de Dados
-------------------------------------
Define as regras de validação Pydantic para os registros das entidades
de Contratos de Energia, Preços de Mercado e Limites de Crédito.
"""

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, StrictFloat, StrictInt

# Submercados válidos no SIN (Sistema Interligado Nacional)
SubmarketType = Literal["SE", "S", "NE", "N"]
OperationType = Literal["BUY", "SELL"]


class ContractSchema(BaseModel):
    """Validação individual para contratos de compra/venda de energia."""

    contract_id: str = Field(..., min_length=1, description="Identificador único do contrato")
    counterparty_id: str = Field(..., min_length=1, description="ID da contraparte")
    submarket: SubmarketType = Field(..., description="Submercado (SE, S, NE, N)")
    type: OperationType = Field(..., description="Tipo da operação (BUY ou SELL)")
    volume_mwm: float = Field(..., gt=0, description="Volume em MW médio (deve ser positivo)")
    strike_price_brl: float = Field(
        ..., gt=0, description="Preço de contrato em R$/MWh (deve ser positivo)"
    )
    start_date: date = Field(..., description="Data de início do suprimento")
    end_date: date = Field(..., description="Data de fim do suprimento")


class MarketPriceSchema(BaseModel):
    """Validação para a curva de preços de mercado (PLD / MtM)."""

    submarket: SubmarketType
    reference_month: str = Field(
        ..., pattern=r"^\d{4}-\d{2}$", description="Mês de referência formato YYYY-MM"
    )
    price_brl: float = Field(..., gt=0, description="Preço de mercado em R$/MWh")


class CounterpartyLimitSchema(BaseModel):
    """Validação para os limites de crédito concedidos por contraparte."""

    counterparty_id: str = Field(..., min_length=1)
    credit_limit_brl: float = Field(..., ge=0, description="Limite de crédito em R$")
