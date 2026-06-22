"""
Modelo de Recuperação da Informação - Busca de Estados por Similaridade
Utiliza TF-IDF + Similaridade de Cosseno
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Carregar dados
df = pd.read_parquet("data/processed/base_integrada.parquet")

print("=" * 60)
print(" MODELO DE RECUPERAÇÃO DA INFORMAÇÃO")
print(" Busca de estados por similaridade de características")
print("=" * 60)


def criar_documento(row):
    doc = f"""
    Estado: {row["uf"]}
    Região: {row["regiao"]}
    Profissionais: {row["total_profissionais"]}
    Renda média: R$ {row["renda_media"]:.0f}
    Custo de vida: {row["indice_custo_vida"]:.2f}
    PIB per capita: R$ {row["pib_per_capita"]:.0f}
    IDH: {row["idh"]:.3f}
    Poder de compra: {row["poder_compra"]:.2f}
    """
    return doc


print("\n Criando documentos para cada estado...")
df["documento"] = df.apply(criar_documento, axis=1)


print("\n Criando matriz TF-IDF...")
vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
tfidf_matrix = vectorizer.fit_transform(df["documento"])

print(f"   Matriz criada: {tfidf_matrix.shape}")
print(f"   Número de estados: {tfidf_matrix.shape[0]}")
print(f"   Número de termos: {tfidf_matrix.shape[1]}")


def buscar_estados_similares(uf_referencia, top_n=5):
    # Verificar se o estado existe
    if uf_referencia not in df["uf"].values:
        print(f"   ⚠️ Estado '{uf_referencia}' não encontrado na base.")
        return pd.DataFrame()

    idx = df[df["uf"] == uf_referencia].index[0]
    similaridades = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()

    resultados = pd.DataFrame(
        {
            "uf": df["uf"],
            "estado": df["estado_x"],
            "similaridade": similaridades,
            "total_profissionais": df["total_profissionais"],
            "renda_media": df["renda_media"],
            "indice_custo_vida": df["indice_custo_vida"],
            "regiao": df["regiao"],
        }
    )

    resultados = resultados[resultados["uf"] != uf_referencia]
    resultados = resultados.sort_values("similaridade", ascending=False)
    return resultados.head(top_n)


print("\n TESTANDO O MODELO DE BUSCA:")

# Listar estados disponíveis
estados_disponiveis = sorted(df["uf"].unique().tolist())
print(f"Estados disponíveis para busca: {estados_disponiveis}")

# Estados para buscar (apenas os que existem)
estados_busca = ["SP", "DF", "BA", "AM", "RS"]
estados_busca = [uf for uf in estados_busca if uf in df["uf"].values]
print(f"Estados que serão testados: {estados_busca}")

for uf in estados_busca:
    print(f"\n{'=' * 50}")
    print(f"Estado referência: {uf}")
    print(f"{'=' * 50}")

    resultados = buscar_estados_similares(uf, top_n=5)

    if resultados.empty:
        print(f"   ⚠️ Nenhum resultado encontrado para {uf}")
        continue

    print("\nEstados mais similares:")
    print(
        f"{'UF':<6} | {'Similaridade':<12} | {'Profissionais':<12} | {'Renda':<8} | {'Região'}"
    )
    print("-" * 60)

    for _, row in resultados.iterrows():
        print(
            f"{row['uf']:<6} | {row['similaridade']:.4f}       | {int(row['total_profissionais']):<12} | R${row['renda_media']:.0f}   | {row['regiao']}"
        )

    print(
        f"\n O estado {uf} é mais similar a {resultados.iloc[0]['uf']} "
        f"(similaridade: {resultados.iloc[0]['similaridade']:.4f})"
    )


print("\n" + "=" * 60)
print(" ANÁLISE DO MODELO TF-IDF")
print("=" * 60)

print(f"\n Estatísticas da matriz TF-IDF:")
print(f"   Número de estados: {tfidf_matrix.shape[0]}")
print(f"   Número de termos: {tfidf_matrix.shape[1]}")
print(
    f"   Densidade: {tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1]) * 100:.2f}%"
)

feature_names = vectorizer.get_feature_names_out()
tfidf_means = np.array(tfidf_matrix.mean(axis=0)).flatten()
top_terms = sorted(zip(feature_names, tfidf_means), key=lambda x: x[1], reverse=True)[
    :10
]

print(f"\n Termos mais relevantes (TF-IDF mais alto):")
print(f"{'Termo':<20} | {'TF-IDF Médio'}")
print("-" * 40)
for termo, score in top_terms:
    print(f"{termo:<20} | {score:.4f}")


print("\n MATRIZ DE SIMILARIDADE (top 5 estados):")

top_estados = df.nlargest(5, "total_profissionais")["uf"].tolist()
print(f"Estados: {top_estados}")

idx_top = [df[df["uf"] == uf].index[0] for uf in top_estados]
sim_matrix = cosine_similarity(tfidf_matrix[idx_top])

print("\nMatriz de Similaridade:")
print("         " + "  ".join([f"{uf:>8}" for uf in top_estados]))
for i, uf1 in enumerate(top_estados):
    linha = f"{uf1:>8} "
    for j in range(len(top_estados)):
        linha += f"{sim_matrix[i][j]:.3f}   "
    print(linha)


print("\n SALVANDO RESULTADOS...")

resultados_completos = []
for uf in df["uf"]:
    resultados = buscar_estados_similares(uf, top_n=3)
    if not resultados.empty:
        for _, row in resultados.iterrows():
            resultados_completos.append(
                {
                    "uf_referencia": uf,
                    "uf_similar": row["uf"],
                    "similaridade": row["similaridade"],
                    "total_profissionais": row["total_profissionais"],
                }
            )

if resultados_completos:
    df_resultados = pd.DataFrame(resultados_completos)
    Path("docs").mkdir(exist_ok=True)
    df_resultados.to_csv("docs/resultados_busca.csv", index=False)
    print(f" Resultados salvos em: docs/resultados_busca.csv")
else:
    print(" Nenhum resultado para salvar.")


print("\n" + "=" * 60)
print(" MODELO DE RI APLICADO COM SUCESSO!")
print("=" * 60)
print(f"   Modelo: TF-IDF + Similaridade de Cosseno")
print(f"   Estados analisados: {len(df)}")
print("=" * 60)
