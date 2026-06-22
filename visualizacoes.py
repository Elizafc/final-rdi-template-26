"""
Visualizações para o relatório final - Salários vs Custo de Vida por Estado
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configurar estilo
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Carregar dados
df = pd.read_parquet("data/processed/base_integrada.parquet")

print("📊 GERANDO VISUALIZAÇÕES...")
print(f"Dados: {len(df)} estados x {len(df.columns)} colunas")

# Criar pasta para figuras
Path("docs/figuras").mkdir(parents=True, exist_ok=True)


# ============================================
# VISUALIZAÇÃO 1: Top 10 Estados com mais profissionais
# ============================================
fig, ax = plt.subplots(figsize=(12, 6))
top10 = df.nlargest(10, "total_profissionais")
cores = sns.color_palette("viridis", len(top10))
bars = ax.bar(top10["uf"], top10["total_profissionais"], color=cores)

# Adicionar valores nas barras
for bar, valor in zip(bars, top10["total_profissionais"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 5,
        f"{int(valor)}",
        ha="center",
        va="bottom",
        fontsize=10,
    )

ax.set_title(
    "Top 10 Estados com Mais Profissionais de Dados", fontsize=16, fontweight="bold"
)
ax.set_xlabel("Estado", fontsize=12)
ax.set_ylabel("Número de Profissionais", fontsize=12)
plt.tight_layout()
plt.savefig("docs/figuras/top10_profissionais.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✅ Top 10 profissionais salvo")


# ============================================
# VISUALIZAÇÃO 2: Relação Profissionais vs Custo de Vida
# ============================================
fig, ax = plt.subplots(figsize=(12, 7))

# Scatter plot com tamanho proporcional à população
scatter = ax.scatter(
    df["indice_custo_vida"],
    df["total_profissionais"],
    s=df["populacao"] / 100000,
    alpha=0.6,
    c=df["renda_media"],
    cmap="RdYlGn",
    edgecolors="black",
    linewidth=0.5,
)

# Adicionar labels dos estados
for i, row in df.iterrows():
    ax.annotate(
        row["uf"],
        (row["indice_custo_vida"], row["total_profissionais"]),
        fontsize=9,
        ha="center",
        va="bottom",
    )

ax.set_xlabel("Índice de Custo de Vida", fontsize=12)
ax.set_ylabel("Total de Profissionais", fontsize=12)
ax.set_title(
    "Profissionais de Dados vs Custo de Vida por Estado", fontsize=14, fontweight="bold"
)

# Adicionar legenda
cbar = plt.colorbar(scatter)
cbar.set_label("Renda Média (R$)", fontsize=10)

plt.tight_layout()
plt.savefig("docs/figuras/profissionais_vs_custo.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✅ Profissionais vs Custo salvo")


# ============================================
# VISUALIZAÇÃO 3: Matriz de Correlação
# ============================================
fig, ax = plt.subplots(figsize=(12, 10))

# Selecionar colunas numéricas
colunas_numericas = [
    "total_profissionais",
    "populacao",
    "pib_per_capita",
    "indice_custo_vida",
    "renda_media",
    "poder_compra",
    "idh",
    "profissionais_por_100k",
    "atratividade",
]

corr = df[colunas_numericas].corr()

# Mapa de calor
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8},
)

ax.set_title(
    "Matriz de Correlação - Indicadores por Estado", fontsize=14, fontweight="bold"
)
plt.tight_layout()
plt.savefig("docs/figuras/matriz_correlacao.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✅ Matriz de correlação salva")


# ============================================
# VISUALIZAÇÃO 4: Profissionais por Região
# ============================================
fig, ax = plt.subplots(figsize=(10, 6))

# Agrupar por região
regiao_df = (
    df.groupby("regiao")
    .agg({"total_profissionais": "sum", "uf": "count"})
    .reset_index()
)
regiao_df.rename(columns={"uf": "num_estados"}, inplace=True)

# Gráfico de barras
cores_regiao = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
bars = ax.bar(regiao_df["regiao"], regiao_df["total_profissionais"], color=cores_regiao)

# Adicionar valores
for bar, valor in zip(bars, regiao_df["total_profissionais"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 10,
        f"{int(valor)}",
        ha="center",
        va="bottom",
        fontsize=10,
    )

ax.set_title(
    "Distribuição de Profissionais de Dados por Região", fontsize=14, fontweight="bold"
)
ax.set_xlabel("Região", fontsize=12)
ax.set_ylabel("Total de Profissionais", fontsize=12)
plt.tight_layout()
plt.savefig("docs/figuras/profissionais_por_regiao.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✅ Profissionais por região salvo")


# ============================================
# VISUALIZAÇÃO 5: Relação PIB e Profissionais
# ============================================
fig, ax = plt.subplots(figsize=(12, 7))

# Scatter plot
scatter = ax.scatter(
    df["pib_per_capita"],
    df["total_profissionais"],
    s=df["populacao"] / 100000,
    alpha=0.6,
    c=df["indice_custo_vida"],
    cmap="plasma",
    edgecolors="black",
    linewidth=0.5,
)

# Labels
for i, row in df.iterrows():
    ax.annotate(
        row["uf"],
        (row["pib_per_capita"], row["total_profissionais"]),
        fontsize=9,
        ha="center",
        va="bottom",
    )

# Linha de tendência
z = np.polyfit(df["pib_per_capita"], df["total_profissionais"], 1)
p = np.poly1d(z)
ax.plot(
    df["pib_per_capita"], p(df["pib_per_capita"]), "r--", alpha=0.5, label="Tendência"
)

ax.set_xlabel("PIB per capita (R$)", fontsize=12)
ax.set_ylabel("Total de Profissionais", fontsize=12)
ax.set_title(
    "Relação entre PIB e Profissionais de Dados", fontsize=14, fontweight="bold"
)

cbar = plt.colorbar(scatter)
cbar.set_label("Custo de Vida", fontsize=10)
ax.legend()

plt.tight_layout()
plt.savefig("docs/figuras/pib_vs_profissionais.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✅ PIB vs profissionais salvo")


# ============================================
# VISUALIZAÇÃO 6: Ranking de Atratividade
# ============================================
fig, ax = plt.subplots(figsize=(12, 7))

# Ordenar por atratividade
df_ordenado = df.sort_values("atratividade", ascending=True)

# Barras horizontais
cores = sns.color_palette("coolwarm", len(df_ordenado))
bars = ax.barh(df_ordenado["uf"], df_ordenado["atratividade"], color=cores)

# Adicionar valores
for bar, valor in zip(bars, df_ordenado["atratividade"]):
    ax.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{valor:.2f}",
        ha="left",
        va="center",
        fontsize=9,
    )

ax.set_title(
    "Ranking de Atratividade dos Estados para Profissionais de Dados",
    fontsize=14,
    fontweight="bold",
)
ax.set_xlabel("Índice de Atratividade (Renda / Custo²)", fontsize=12)
ax.set_ylabel("Estado", fontsize=12)
plt.tight_layout()
plt.savefig("docs/figuras/ranking_atratividade.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✅ Ranking de atratividade salvo")


print("\n" + "=" * 50)
print("✅ TODAS AS VISUALIZAÇÕES FORAM GERADAS!")
print(f"📁 Pasta: docs/figuras/")
print("=" * 50)
