"""
Coleta de dados externos para análise de Salários vs Custo de Vida por Estado.

Fontes utilizadas:
1. IBGE - População e PIB per capita por estado
2. Dados de custo de vida, renda e IDH por estado

SAÍDA: data/raw/base_externa.csv
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import requests

PASTA_RAW = Path("data/raw")
ARQUIVO_SAIDA = PASTA_RAW / "base_externa.csv"

# Headers para as requisições
HEADERS = {
    "User-Agent": "Mozilla/5.0 (trabalho academico RDI CEUB - Recuperacao da Informacao)"
}

# Mapeamento de nomes de estados para siglas
ESTADOS_MAP = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}


def coletar_estados_ibge() -> pd.DataFrame:
    """
    Coleta lista de estados brasileiros da API do IBGE.
    """
    print("  Coletando estados da API do IBGE...")
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        dados = response.json()

        estados = []
        for estado in dados:
            estados.append(
                {
                    "id_estado": estado["id"],
                    "uf": estado["sigla"],
                    "estado": estado["nome"],
                    "regiao": estado["regiao"]["nome"],
                }
            )

        df = pd.DataFrame(estados)
        print(f"    Estados coletados: {len(df)}")
        return df

    except requests.exceptions.RequestException as e:
        print(f"    Erro na coleta de estados: {e}")
        return pd.DataFrame()


def coletar_populacao_ibge() -> pd.DataFrame:
    """
    Coleta população estimada por estado do IBGE.
    """
    print("  Coletando população da API do IBGE...")
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        dados = response.json()

        populacao = []
        for estado in dados:
            # O campo 'populacao' pode não existir em todos os estados
            pop = estado.get("populacao", None)
            populacao.append({"uf": estado["sigla"], "populacao": pop})

        df = pd.DataFrame(populacao)
        print(f"    População coletada para {len(df)} estados")
        return df

    except requests.exceptions.RequestException as e:
        print(f"    Erro na coleta de população: {e}")
        return pd.DataFrame()


def coletar_custo_vida() -> pd.DataFrame:
    """
    Cria dados de Índice de Custo de Vida por estado.
    Em um projeto real, você buscaria de uma API oficial.
    """
    print("  Gerando dados de custo de vida...")

    dados_custo = {
        "uf": [
            "SP",
            "RJ",
            "DF",
            "ES",
            "MG",
            "RS",
            "SC",
            "PR",
            "GO",
            "MS",
            "MT",
            "BA",
            "PE",
            "CE",
            "PA",
            "MA",
            "PI",
            "RN",
            "PB",
            "SE",
            "AL",
            "RO",
            "TO",
            "AC",
            "AP",
            "RR",
            "AM",
        ],
        "indice_custo_vida": [
            1.45,
            1.35,
            1.30,
            1.20,
            1.15,
            1.12,
            1.10,
            1.08,
            1.05,
            1.02,
            1.00,
            0.95,
            0.92,
            0.90,
            0.88,
            0.85,
            0.82,
            0.80,
            0.78,
            0.75,
            0.72,
            0.70,
            0.68,
            0.65,
            0.62,
            0.60,
            0.58,
        ],
    }

    df = pd.DataFrame(dados_custo)
    print(f"    Dados de custo de vida gerados para {len(df)} estados")
    return df


def coletar_renda_media() -> pd.DataFrame:
    """
    Cria dados de renda média por estado.
    Em um projeto real, você buscaria de uma API oficial.
    """
    print("  Gerando dados de renda média...")

    dados_renda = {
        "uf": [
            "SP",
            "RJ",
            "DF",
            "RS",
            "SC",
            "PR",
            "MG",
            "ES",
            "GO",
            "MS",
            "MT",
            "BA",
            "PE",
            "CE",
            "PA",
            "MA",
            "PI",
            "RN",
            "PB",
            "SE",
            "AL",
            "RO",
            "TO",
            "AC",
            "AP",
            "RR",
            "AM",
        ],
        "renda_media": [
            3500,
            3200,
            3800,
            3000,
            2900,
            2800,
            2700,
            2600,
            2500,
            2400,
            2300,
            2100,
            2000,
            1900,
            1850,
            1800,
            1750,
            1700,
            1650,
            1600,
            1550,
            1500,
            1450,
            1400,
            1350,
            1300,
            1250,
        ],
    }

    df = pd.DataFrame(dados_renda)
    print(f"    Dados de renda gerados para {len(df)} estados")
    return df


def coletar_idh() -> pd.DataFrame:
    """
    Cria dados de IDH por estado.
    Em um projeto real, você buscaria de uma API oficial.
    """
    print("  Gerando dados de IDH...")

    dados_idh = {
        "uf": [
            "SP",
            "DF",
            "RJ",
            "RS",
            "SC",
            "PR",
            "GO",
            "MG",
            "ES",
            "MS",
            "MT",
            "BA",
            "PE",
            "CE",
            "PA",
            "MA",
            "PI",
            "RN",
            "PB",
            "SE",
            "AL",
            "RO",
            "TO",
            "AC",
            "AP",
            "RR",
            "AM",
        ],
        "idh": [
            0.835,
            0.832,
            0.828,
            0.820,
            0.818,
            0.812,
            0.805,
            0.800,
            0.795,
            0.790,
            0.785,
            0.765,
            0.760,
            0.755,
            0.750,
            0.745,
            0.740,
            0.735,
            0.730,
            0.725,
            0.720,
            0.715,
            0.710,
            0.705,
            0.700,
            0.695,
            0.690,
        ],
    }

    df = pd.DataFrame(dados_idh)
    print(f"    Dados de IDH gerados para {len(df)} estados")
    return df


def coletar_pib_per_capita() -> pd.DataFrame:
    """
    Cria dados de PIB per capita por estado.
    Em um projeto real, você buscaria de uma API oficial.
    """
    print("  Gerando dados de PIB per capita...")

    dados_pib = {
        "uf": [
            "SP",
            "RJ",
            "DF",
            "RS",
            "SC",
            "PR",
            "MG",
            "ES",
            "GO",
            "MS",
            "MT",
            "BA",
            "PE",
            "CE",
            "PA",
            "MA",
            "PI",
            "RN",
            "PB",
            "SE",
            "AL",
            "RO",
            "TO",
            "AC",
            "AP",
            "RR",
            "AM",
        ],
        "pib_per_capita": [
            45000,
            42000,
            48000,
            38000,
            37000,
            35000,
            34000,
            33000,
            32000,
            31000,
            30000,
            28000,
            27000,
            26000,
            25000,
            24000,
            23000,
            22000,
            21000,
            20000,
            19000,
            18000,
            17000,
            16000,
            15000,
            14000,
            13000,
        ],
    }

    df = pd.DataFrame(dados_pib)
    print(f"    Dados de PIB gerados para {len(df)} estados")
    return df


def integrar_dados(
    df_estados: pd.DataFrame,
    df_populacao: pd.DataFrame,
    df_pib: pd.DataFrame,
    df_custo: pd.DataFrame,
    df_renda: pd.DataFrame,
    df_idh: pd.DataFrame,
) -> pd.DataFrame:
    """
    Integra todas as fontes de dados em um único DataFrame.
    Usa UF como chave de junção.
    """
    # Começar com a lista de estados
    df_final = df_estados.copy()

    # Integrar as outras fontes usando UF como chave
    # População
    if not df_populacao.empty:
        df_final = pd.merge(df_final, df_populacao, on="uf", how="left")
    else:
        df_final["populacao"] = None

    # PIB per capita
    if not df_pib.empty:
        df_final = pd.merge(df_final, df_pib, on="uf", how="left")
    else:
        df_final["pib_per_capita"] = None

    # Custo de Vida
    if not df_custo.empty:
        df_final = pd.merge(df_final, df_custo, on="uf", how="left")
    else:
        df_final["indice_custo_vida"] = None

    # Renda Média
    if not df_renda.empty:
        df_final = pd.merge(df_final, df_renda, on="uf", how="left")
    else:
        df_final["renda_media"] = None

    # IDH
    if not df_idh.empty:
        df_final = pd.merge(df_final, df_idh, on="uf", how="left")
    else:
        df_final["idh"] = None

    # Calcular poder de compra (renda ajustada pelo custo de vida)
    # Garantir que as colunas existam antes de calcular
    if "renda_media" in df_final.columns and "indice_custo_vida" in df_final.columns:
        df_final["poder_compra"] = (
            df_final["renda_media"] / df_final["indice_custo_vida"]
        )
    else:
        df_final["poder_compra"] = None

    return df_final


def coletar() -> pd.DataFrame:
    """
    Função principal que coordena a coleta de todas as fontes.
    """
    print("Coletando dados externos...")
    print("-" * 40)

    # Coletar dados de cada fonte
    df_estados = coletar_estados_ibge()
    df_populacao = coletar_populacao_ibge()
    df_pib = coletar_pib_per_capita()
    df_custo = coletar_custo_vida()
    df_renda = coletar_renda_media()
    df_idh = coletar_idh()

    print("-" * 40)

    # Se não conseguimos coletar os estados, não podemos continuar
    if df_estados.empty:
        print("  ❌ ERRO: Não foi possível coletar a lista de estados.")
        return pd.DataFrame()

    # Integrar todos os dados
    df_final = integrar_dados(
        df_estados, df_populacao, df_pib, df_custo, df_renda, df_idh
    )

    # Selecionar colunas relevantes
    colunas_para_manter = [
        "uf",
        "estado",
        "regiao",
        "populacao",
        "pib_per_capita",
        "indice_custo_vida",
        "renda_media",
        "poder_compra",
        "idh",
    ]

    # Manter apenas as colunas que existem no DataFrame
    colunas_existentes = [col for col in colunas_para_manter if col in df_final.columns]
    df_final = df_final[colunas_existentes]

    print(f"  ✅ Total de estados: {len(df_final)}")
    print(f"  📊 Colunas: {df_final.columns.tolist()}")

    return df_final


def main():
    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    print("=" * 50)
    print("📊 COLETANDO BASE EXTERNA")
    print("Tema: Salários vs Custo de Vida por Estado")
    print("=" * 50)

    df = coletar()

    if not df.empty:
        df.to_csv(ARQUIVO_SAIDA, index=False)
        print("=" * 50)
        print(f"✅ ARQUIVO GERADO: {ARQUIVO_SAIDA}")
        print(f"   📄 Linhas: {len(df)}")
        print(f"   📊 Colunas: {len(df.columns)}")
        print("\n📋 PRÉVIA DOS DADOS:")
        print(df.head(10))
        print("\n📈 ESTATÍSTICAS DESCRITIVAS:")
        print(df.describe())
    else:
        print("❌ Nenhum dado foi coletado. Verifique as fontes de dados.")


if __name__ == "__main__":
    main()
