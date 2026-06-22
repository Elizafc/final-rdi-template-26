"""
Limpeza, padronização e INTEGRAÇÃO das duas bases.

Tema: Salários vs Custo de Vida por Estado

ENTRADAS:
  data/processed/dados_state_of_data_consolidados.parquet
  data/raw/base_externa.csv
SAÍDA:
  data/processed/base_integrada.parquet

Rode com:  python src/limpeza/integra.py
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

PROC = Path("data/processed")
RAW = Path("data/raw")

# Mapeamento de nomes de estados para siglas
ESTADOS_PARA_SIGLA: Dict[str, str] = {
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

SIGLAS_PARA_ESTADO: Dict[str, str] = {v: k for k, v in ESTADOS_PARA_SIGLA.items()}
UF_VALIDAS: List[str] = list(ESTADOS_PARA_SIGLA.values())


def ler_parquet_robusto(caminho: Union[Path, str]) -> pd.DataFrame:
    """Lê parquet contornando incompatibilidades pandas/pyarrow conhecidas."""
    caminho_str = str(caminho)
    try:
        import pyarrow.parquet as pq

        return pq.read_table(caminho_str).to_pandas()
    except Exception:
        pass
    try:
        return pd.read_parquet(caminho_str, engine="fastparquet")
    except Exception:
        return pd.read_parquet(caminho_str)


def identificar_colunas_uf(df: pd.DataFrame) -> Optional[str]:
    """
    Identifica qual coluna contém a Unidade Federativa (UF).
    Retorna o nome da coluna ou None se não encontrar.
    """
    padroes_uf: List[str] = [
        "uf",
        "UF",
        "estado",
        "Estado",
        "state",
        "State",
        "sigla",
        "Sigla",
        "regiao",
        "Regiao",
        "uf_estado",
        "Estado onde mora",
        "estado onde mora",
        "estado_mora",
    ]

    for col in df.columns:
        col_str = str(col)
        col_lower = col_str.lower()
        for padrao in padroes_uf:
            if padrao.lower() in col_lower:
                print(f"    Encontrou UF na coluna: '{col_str}'")
                return col_str

    return None


def extrair_sigla(valor: str) -> str:
    """
    Extrai a sigla do estado de strings como 'CEARÁ (CE)' ou 'SÃO PAULO (SP)'
    """
    if not isinstance(valor, str):
        return valor

    valor = valor.strip().upper()

    # Tentar extrair padrão "NOME (UF)"
    match = re.search(r"\(([A-Z]{2})\)", valor)
    if match:
        return match.group(1)

    # Tentar extrair apenas 2 letras maiúsculas no final
    match = re.search(r"([A-Z]{2})$", valor)
    if match:
        return match.group(1)

    # Se o valor já for uma sigla válida
    if valor in UF_VALIDAS:
        return valor

    # Se o valor for um nome de estado, converter para sigla
    for estado, sigla in ESTADOS_PARA_SIGLA.items():
        if estado.upper() in valor:
            return sigla

    return valor


def padronizar_uf(df: pd.DataFrame, col_uf: str) -> pd.DataFrame:
    """
    Padroniza a coluna de UF para sigla de dois caracteres (AC, SP, etc.)
    """
    df = df.copy()

    # Converter para string
    df[col_uf] = df[col_uf].astype(str)

    # Extrair sigla de cada valor
    df[col_uf] = df[col_uf].apply(extrair_sigla)

    # Remover espaços extras
    df[col_uf] = df[col_uf].str.strip().str.upper()

    return df


def agregar_state_of_data(df_sod: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega os dados do State of Data por UF.
    Calcula métricas relevantes para cada estado.
    """
    print("  Agregando State of Data por UF...")

    # Identificar coluna de UF
    col_uf = identificar_colunas_uf(df_sod)

    if col_uf is None:
        print("  ❌ Não foi possível identificar a coluna UF no State of Data.")
        return pd.DataFrame()

    print(f"    Coluna UF identificada: '{col_uf}'")

    # Padronizar UF (extrair siglas)
    df_sod = padronizar_uf(df_sod, col_uf)

    # Verificar valores únicos após padronização
    uf_unicas = df_sod[col_uf].unique()
    print(f"    Valores únicos após padronização: {len(uf_unicas)}")
    print(f"    Primeiros 10 valores: {uf_unicas[:10]}")

    # Filtrar apenas linhas com UF válida
    df_sod_filtrado = df_sod[df_sod[col_uf].isin(UF_VALIDAS)]

    print(f"    Registros com UF válida: {len(df_sod_filtrado):,}")

    if df_sod_filtrado.empty:
        print("  ❌ Nenhum registro com UF válida encontrado.")
        print(f"  UF válidas esperadas: {UF_VALIDAS}")
        return pd.DataFrame()

    # Agrupar por UF
    contagem = df_sod_filtrado.groupby(col_uf, as_index=False).size()

    # Renomear colunas
    contagem = contagem.rename(columns={col_uf: "uf", "size": "total_profissionais"})

    # Adicionar nome do estado
    contagem["estado"] = contagem["uf"].apply(lambda x: SIGLAS_PARA_ESTADO.get(x, x))

    # Ordenar
    contagem = contagem.sort_values(by=["uf"]).reset_index(drop=True)

    print(f"    Estados agregados: {len(contagem)}")

    return contagem


def integrar_bases(df_sod: pd.DataFrame, df_ext: pd.DataFrame) -> pd.DataFrame:
    """
    Integra as duas bases usando UF como chave.
    """
    print("  Integrando bases...")

    # Agregar State of Data
    df_sod_agregado = agregar_state_of_data(df_sod)

    if df_sod_agregado.empty:
        print("  ❌ Erro: Não foi possível agregar o State of Data.")
        return pd.DataFrame()

    # Preparar base externa
    df_ext = df_ext.copy()

    # Garantir que a base externa tenha UF padronizada
    if "uf" not in df_ext.columns:
        col_uf_ext = identificar_colunas_uf(df_ext)
        if col_uf_ext:
            df_ext = padronizar_uf(df_ext, col_uf_ext)
            df_ext = df_ext.rename(columns={col_uf_ext: "uf"})

    print(f"    State of Data agregado: {df_sod_agregado.shape}")
    print(f"    Base externa: {df_ext.shape}")

    # Fazer o merge das duas bases
    df_integrado = pd.merge(df_sod_agregado, df_ext, on="uf", how="inner")

    print(f"    Estados integrados: {len(df_integrado)}")

    if df_integrado.empty:
        print("  ⚠️ Aviso: Nenhum estado foi integrado. Verifique as UFs.")
        if "uf" in df_sod_agregado.columns:
            print(f"  UFs no State of Data: {df_sod_agregado['uf'].unique().tolist()}")
        if "uf" in df_ext.columns:
            print(f"  UFs na base externa: {df_ext['uf'].unique().tolist()}")
        return pd.DataFrame()

    return df_integrado


def criar_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria métricas derivadas para análise.
    """
    print("  Criando métricas derivadas...")
    df = df.copy()

    # Profissionais per capita
    if "populacao" in df.columns and "total_profissionais" in df.columns:
        df["profissionais_por_100k"] = (
            df["total_profissionais"] / df["populacao"] * 100000
        )

    # Score de atratividade
    if "renda_media" in df.columns and "indice_custo_vida" in df.columns:
        df["atratividade"] = df["renda_media"] / (df["indice_custo_vida"] ** 2)

    # Poder de compra
    if "renda_media" in df.columns and "indice_custo_vida" in df.columns:
        df["poder_compra"] = df["renda_media"] / df["indice_custo_vida"]

    return df


def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpeza final dos dados integrados.
    """
    print("  Limpando dados integrados...")
    df = df.copy()

    # Remover linhas com valores nulos críticos
    colunas_criticas = ["uf", "total_profissionais"]
    colunas_existentes = [col for col in colunas_criticas if col in df.columns]
    if colunas_existentes:
        df = df.dropna(subset=colunas_existentes)

    # Remover duplicatas
    if "uf" in df.columns:
        df = df.drop_duplicates(subset=["uf"])

    # Ordenar por UF
    if "uf" in df.columns:
        df = df.sort_values(by=["uf"]).reset_index(drop=True)

    print(f"    Registros após limpeza: {len(df)}")

    return df


def salvar_relatorio_sumario(df: pd.DataFrame) -> None:
    """
    Gera um relatório sumário das métricas integradas.
    """
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE INTEGRAÇÃO")
    print("=" * 60)

    print(f"\n📄 Total de estados integrados: {len(df)}")
    print(f"📊 Total de colunas: {len(df.columns)}")

    print("\n📊 AMOSTRA DOS DADOS INTEGRADOS:")
    colunas_mostrar = [
        "uf",
        "estado",
        "total_profissionais",
        "renda_media",
        "indice_custo_vida",
        "poder_compra",
    ]
    colunas_mostrar = [col for col in colunas_mostrar if col in df.columns]
    if colunas_mostrar:
        print(df[colunas_mostrar].head(10))
    else:
        print(df.head(10))

    print("\n📈 CORRELAÇÕES PRINCIPAIS:")
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    if "total_profissionais" in colunas_numericas and len(colunas_numericas) > 1:
        try:
            correlacoes = df[colunas_numericas].corr()
            if "total_profissionais" in correlacoes.columns:
                correlacao_total = correlacoes["total_profissionais"].sort_values(
                    ascending=False
                )
                print(correlacao_total)
        except Exception as e:
            print(f"  Erro ao calcular correlações: {e}")

    print("\n" + "=" * 60)


def main() -> None:
    print("=" * 60)
    print("🔗 INTEGRAÇÃO DAS BASES DE DADOS")
    print("Tema: Salários vs Custo de Vida por Estado")
    print("=" * 60)

    print("\n📂 Carregando as duas bases...")

    try:
        df_sod = ler_parquet_robusto(PROC / "dados_state_of_data_consolidados.parquet")
        print(
            f"  ✅ State of Data: {df_sod.shape[0]:,} linhas x {df_sod.shape[1]} colunas"
        )
    except FileNotFoundError:
        print("  ❌ Erro: Arquivo do State of Data não encontrado!")
        print("  Execute primeiro: python src/coleta/consolida_state_of_data.py")
        return

    try:
        df_ext = pd.read_csv(RAW / "base_externa.csv")
        print(
            f"  ✅ Base externa: {df_ext.shape[0]} linhas x {df_ext.shape[1]} colunas"
        )
    except FileNotFoundError:
        print("  ❌ Erro: Arquivo da base externa não encontrado!")
        print("  Execute primeiro: python src/coleta/coleta_externa.py")
        return

    print("\n" + "-" * 60)

    df_integrado = integrar_bases(df_sod, df_ext)

    if df_integrado.empty:
        print("\n❌ Falha na integração. Verifique os dados.")
        return

    df_integrado = limpar_dados(df_integrado)
    df_final = criar_metricas(df_integrado)

    PROC.mkdir(parents=True, exist_ok=True)
    saida = PROC / "base_integrada.parquet"
    df_final.to_parquet(saida, index=False)

    print("\n" + "-" * 60)
    print(f"✅ ARQUIVO GERADO: {saida}")
    print(f"   📄 Dimensões: {df_final.shape[0]} estados x {df_final.shape[1]} colunas")
    print(f"   📊 Colunas: {df_final.columns.tolist()}")

    salvar_relatorio_sumario(df_final)

    print("\n✅ Integração concluída com sucesso!")


if __name__ == "__main__":
    main()
