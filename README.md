# ⚡ W3 Solana Risk (`w3-solana-risk`)

> **Risk Infrastructure for Energy Markets powered by Solana**

Plataforma enxuta de engenharia de dados e **Risk Engine** desenhada para o Mercado Livre de Energia brasileiro. O projeto realiza a ingestão de contratos, curvas de preço (PLD/Forward) e limites de crédito, calcula a posição de risco (_Mark-to-Market_ e Exposição por Contraparte) e gera **evidências criptográficas imutáveis na blockchain Solana**.

---

## 🎯 O Problema & A Solução

No Mercado Livre de Energia, a gestão de risco e precificação depende de acompanhamento diário de exposição financeira e garantias. Processos tradicionais costumam ser opacos e sujeitos a contestação.

O **`w3-solana-risk`** resolve isso em duas camadas:

1. **Off-chain (Data Engine):** Processamento local de alta performance (DuckDB / Polars) para ingestão, tratamento e cálculo de MtM e limites de crédito.
2. **On-chain (Solana):** Registro de _hashes_ SHA-256 da posição de risco diária na **Solana Devnet**, garantindo não repúdio, rastreabilidade e auditabilidade sem expor dados comerciais sensíveis.

---

## 🏗️ Arquitetura do Pipeline

A arquitetura adota o padrão Medallion de engenharia de dados de forma simplificada e local:

---

## 🛠️ Tech Stack

- **Linguagem:** Python 3.11+
- **Gerenciador de Pacotes:** `uv` (Fast Python package installer)
- **Engenharia de Dados & Analítico:** DuckDB, Polars, Pandas, PyArrow
- **Validação de Schemas:** Pydantic
- **Blockchain:** Solana Python SDK (`solana-py`, `solders`) na Devnet
- **Testes & Qualidade:** Pytest
- **Interface Visual:** Streamlit

---

## 📁 Estrutura do Projeto

```text
w3-solana-risk/
├── data/                         # Armazenamento em camadas (Medallion)
│   ├── raw/                      # Arquivos CSV brutos de entrada
│   ├── bronze/                   # Ingestão em Parquet
│   ├── silver/                   # Dados limpos e padronizados
│   └── gold/                     # Posições calculadas e exibições
│
├── src/                          # Código-fonte da aplicação
│   ├── config.py                 # Mapeamento e gestão de caminhos
│   ├── ingestion/                # Ingestão de dados (Bronze)
│   ├── transformation/           # Limpeza e cálculo de horas/MWh (Silver)
│   ├── engine/                   # Motor de cálculo de MtM e Exposição (Gold)
│   └── blockchain/               # Hasher SHA-256 e integração Solana Devnet
│
├── tests/                        # Suíte de testes unitários com pytest
├── app.py                        # Dashboard interativo em Streamlit
├── requirements.txt              # Dependências do projeto
└── README.md                     # Documentação do repositório
```
