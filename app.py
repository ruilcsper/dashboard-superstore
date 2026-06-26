import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --------------------------------------------------
# Configuração da página
# --------------------------------------------------
st.set_page_config(
    page_title="Campanhas online - eCommerce",
    layout="wide"
)

st.title("📊 Campanhas Online - eCommerce")
st.markdown("Dashboard de análise de campanhas | Segmento: **Mulheres 45-54** | Objetivo: **Lead Generation**")

# --------------------------------------------------
# Carregamento dos dados
# --------------------------------------------------
@st.cache_data
def load_data():
    file_name = "tech_advertising_campaigns_dataset_filtered.csv"
    df = pd.read_csv(file_name, header=0)

    target_age_groups = ['45-54']
    target_gender = 'Female'
    campaign_objective = 'Lead Generation'

    filtered_df = df[
        (df['target_audience_age'].isin(target_age_groups)) &
        (df['target_audience_gender'] == target_gender) &
        (df['campaign_objective'] == campaign_objective)
    ]

    selected_columns = [
        'platform', 'ad_placement', 'device_type', 'operating_system',
        'creative_format', 'has_call_to_action', 'creative_emotion',
        'creative_age_days', 'target_audience_age', 'target_audience_gender',
        'start_date', 'hour_of_day', 'campaign_day', 'impressions',
        'clicks', 'conversions', 'CTR', 'CPC', 'conversion_rate', 'CPA'
    ]

    selected_df = filtered_df[selected_columns].copy()
    selected_df['start_date'] = pd.to_datetime(selected_df['start_date'])
    selected_df['has_call_to_action'] = selected_df['has_call_to_action'].map({'true': 1, 'false': 0})

    numeric_cols = ['creative_age_days', 'hour_of_day', 'campaign_day',
                    'impressions', 'clicks', 'conversions', 'CTR', 'CPC', 'conversion_rate', 'CPA']
    for col in numeric_cols:
        selected_df[col] = pd.to_numeric(selected_df[col], errors='coerce')

    category_cols = ['platform', 'ad_placement', 'device_type', 'operating_system',
                     'creative_format', 'creative_emotion', 'target_audience_age', 'target_audience_gender']
    for col in category_cols:
        selected_df[col] = selected_df[col].astype('category')

    return selected_df


df = load_data()

# --------------------------------------------------
# Sidebar com filtros
# --------------------------------------------------
st.sidebar.header("🔎 Filtros")

sorted_platform = sorted(df["platform"].cat.categories.tolist())
platform = st.sidebar.multiselect("Plataformas", options=sorted_platform, default=sorted_platform)

sorted_ad_placement = sorted(df["ad_placement"].cat.categories.tolist())
ad_placement = st.sidebar.multiselect("Localização do anúncio", options=sorted_ad_placement, default=sorted_ad_placement)

sorted_creative_format = sorted(df["creative_format"].cat.categories.tolist())
creative_format = st.sidebar.multiselect("Formato do anúncio", options=sorted_creative_format, default=sorted_creative_format)

sorted_device = sorted(df["device_type"].cat.categories.tolist())
device_type = st.sidebar.multiselect("Dispositivo", options=sorted_device, default=sorted_device)

sorted_emotion = sorted(df["creative_emotion"].cat.categories.tolist())
creative_emotion = st.sidebar.multiselect("Emoção criativa", options=sorted_emotion, default=sorted_emotion)

sorted_hour_of_day = sorted(df["hour_of_day"].dropna().unique())
hour_of_day_range = st.sidebar.slider(
    "Hora do dia",
    min_value=int(min(sorted_hour_of_day)),
    max_value=int(max(sorted_hour_of_day)),
    value=(int(min(sorted_hour_of_day)), int(max(sorted_hour_of_day)))
)

years = sorted(df["start_date"].dt.year.dropna().unique())
year_range = st.sidebar.slider(
    "Ano",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# --------------------------------------------------
# Aplicar filtros
# --------------------------------------------------
filtered_df = df[
    (df["platform"].isin(platform)) &
    (df["ad_placement"].isin(ad_placement)) &
    (df["creative_format"].isin(creative_format)) &
    (df["device_type"].isin(device_type)) &
    (df["creative_emotion"].isin(creative_emotion)) &
    (df["hour_of_day"].between(hour_of_day_range[0], hour_of_day_range[1])) &
    (df["start_date"].dt.year.between(year_range[0], year_range[1]))
]

# --------------------------------------------------
# SECÇÃO 1: KPIs
# --------------------------------------------------
st.subheader("📌 Indicadores Chave de Desempenho (KPIs)")

total_impressions   = filtered_df["impressions"].sum()
total_clicks        = filtered_df["clicks"].sum()
total_conversions   = filtered_df["conversions"].sum()
avg_ctr             = filtered_df["CTR"].mean()
avg_cpc             = filtered_df["CPC"].mean()
avg_conversion_rate = filtered_df["conversion_rate"].mean()
avg_cpa             = filtered_df["CPA"].mean()

overall_ctr      = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
overall_cvr      = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
clicks_per_conv  = (total_clicks / total_conversions) if total_conversions > 0 else 0
cta_rate         = filtered_df["has_call_to_action"].mean() * 100
avg_creative_age = filtered_df["creative_age_days"].mean()

st.markdown("**Volume & Alcance**")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de Impressões",   f"{total_impressions:,.0f}")
c2.metric("Total de Cliques",      f"{total_clicks:,.0f}")
c3.metric("Total de Conversões",   f"{total_conversions:,.0f}")
c4.metric("Cliques por Conversão", f"{clicks_per_conv:.1f}")

st.markdown("**Eficiência & Custo**")
c5, c6, c7, c8 = st.columns(4)
c5.metric("CTR Global",               f"{overall_ctr:.2f}%")
c6.metric("Taxa de Conversão Global", f"{overall_cvr:.2f}%")
c7.metric("CPC Médio",                f"${avg_cpc:.2f}")
c8.metric("CPA Médio",                f"${avg_cpa:.2f}")

st.markdown("**Qualidade Criativa**")
c9, c10, c11, c12 = st.columns(4)
c9.metric("CTR Médio (por campanha)",        f"{avg_ctr:.2f}%")
c10.metric("Conv. Rate Médio (por camp.)",   f"{avg_conversion_rate:.2f}%")
c11.metric("Anúncios com CTA (%)",           f"{cta_rate:.1f}%")
c12.metric("Idade Média do Criativo (dias)", f"{avg_creative_age:.0f}")

st.divider()

# --------------------------------------------------
# SECÇÃO 2: GRÁFICOS BASE
# --------------------------------------------------

# Gráfico 1 – CTR médio por Hora do Dia
st.subheader("📈 CTR médio por Hora do Dia")
ctr_by_hour = filtered_df.groupby("hour_of_day")["CTR"].mean().reset_index()
fig1 = px.line(ctr_by_hour, x="hour_of_day", y="CTR", markers=True,
               labels={"hour_of_day": "Hora do Dia", "CTR": "CTR Médio (%)"},
               color_discrete_sequence=["#01696f"])
fig1.update_layout(template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# Gráfico 2 – Taxa de Conversão por Plataforma
st.subheader("🏆 Taxa de Conversão Média por Plataforma")
conv_by_platform = (filtered_df.groupby("platform", observed=True)["conversion_rate"]
                    .mean().reset_index().sort_values("conversion_rate", ascending=False))
fig2 = px.bar(conv_by_platform, x="platform", y="conversion_rate", color="platform",
              labels={"platform": "Plataforma", "conversion_rate": "Taxa de Conversão Média (%)"},
              color_discrete_sequence=px.colors.qualitative.Set2)
fig2.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Gráfico 3 – Heatmap: Tipo de Media × Plataforma × Conversões
st.subheader("🔥 Correlação: Tipo de Media por Plataforma vs. Conversões")
st.caption("Soma total de conversões por combinação de Formato de Anúncio e Plataforma")
conv_heatmap = (filtered_df.groupby(["creative_format", "platform"], observed=True)["conversions"]
                .sum().reset_index())
heatmap_pivot = conv_heatmap.pivot(index="creative_format", columns="platform",
                                    values="conversions").fillna(0)
fig3 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=heatmap_pivot.columns.tolist(),
    y=heatmap_pivot.index.tolist(),
    colorscale="Teal",
    text=np.round(heatmap_pivot.values, 0).astype(int),
    texttemplate="%{text}",
    colorbar=dict(title="Conversões")
))
fig3.update_layout(template="plotly_white", xaxis_title="Plataforma",
                   yaxis_title="Formato do Anúncio")
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Gráfico 4 – Box Plot: Plataforma × Taxa de Conversão
st.subheader("📦 Distribuição da Taxa de Conversão por Plataforma")
st.caption("Mediana, dispersão e outliers da taxa de conversão por plataforma")
fig4 = px.box(filtered_df, x="platform", y="conversion_rate", color="platform",
              labels={"platform": "Plataforma", "conversion_rate": "Taxa de Conversão (%)"},
              color_discrete_sequence=px.colors.qualitative.Set2)
fig4.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Gráfico 5 – Scatter: CPC vs. Taxa de Conversão
st.subheader("💡 CPC vs. Taxa de Conversão por Plataforma")
st.caption("Relação custo-eficiência — bolhas dimensionadas pelo total de conversões")
scatter_df = filtered_df.dropna(subset=["CPC", "conversion_rate", "conversions"])
fig5 = px.scatter(scatter_df, x="CPC", y="conversion_rate", color="platform",
                  size="conversions", hover_data=["creative_format", "ad_placement"],
                  labels={"CPC": "Custo por Clique ($)", "conversion_rate": "Taxa de Conversão (%)",
                          "platform": "Plataforma"},
                  color_discrete_sequence=px.colors.qualitative.Set2, opacity=0.7)
fig5.update_layout(template="plotly_white")
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# --------------------------------------------------
# SECÇÃO 3: ANÁLISE AVANÇADA
# --------------------------------------------------
st.header("🆕 Análise Avançada")

# Gráfico 6 – Funil de Conversão por Plataforma
st.subheader("🔽 Funil de Conversão por Plataforma")
st.caption("Visualização das perdas em cada etapa do funil por plataforma")
funnel_data = (filtered_df.groupby("platform", observed=True)
               .agg(Impressões=("impressions", "sum"),
                    Cliques=("clicks", "sum"),
                    Conversões=("conversions", "sum"))
               .reset_index())
funnel_melted = funnel_data.melt(id_vars="platform", var_name="Etapa", value_name="Volume")
etapa_order = ["Impressões", "Cliques", "Conversões"]
funnel_melted["Etapa"] = pd.Categorical(funnel_melted["Etapa"], categories=etapa_order, ordered=True)
fig6 = px.bar(funnel_melted.sort_values("Etapa"), x="platform", y="Volume",
              color="Etapa", barmode="group",
              labels={"platform": "Plataforma", "Volume": "Volume Total"},
              color_discrete_sequence=["#4f98a3", "#01696f", "#0f3638"])
fig6.update_layout(template="plotly_white")
st.plotly_chart(fig6, use_container_width=True)

st.divider()

# Gráfico 7 – CPA vs. Conversões por Formato
st.subheader("💰 CPA vs. Total de Conversões por Formato de Anúncio")
st.caption("Formatos no canto inferior direito são os mais eficientes: alto volume a baixo custo")
cpa_conv = (filtered_df.groupby("creative_format", observed=True)
            .agg(CPA_medio=("CPA", "mean"),
                 Total_Conversoes=("conversions", "sum"),
                 CTR_medio=("CTR", "mean"))
            .reset_index())
fig7 = px.scatter(cpa_conv, x="CPA_medio", y="Total_Conversoes",
                  size="CTR_medio", color="creative_format", text="creative_format",
                  labels={"CPA_medio": "CPA Médio ($)", "Total_Conversoes": "Total de Conversões",
                          "CTR_medio": "CTR Médio (%)", "creative_format": "Formato"},
                  color_discrete_sequence=px.colors.qualitative.Safe)
fig7.update_traces(textposition="top center")
fig7.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig7, use_container_width=True)

st.divider()

# Gráfico 8 – Heatmap: Emoção Criativa × Plataforma × Taxa de Conversão
st.subheader("🎭 Emoção Criativa por Plataforma vs. Taxa de Conversão Média")
st.caption("Qual a emoção do criativo que gera maior taxa de conversão em cada plataforma?")
emo_platform = (filtered_df.groupby(["creative_emotion", "platform"], observed=True)["conversion_rate"]
                .mean().reset_index())
emo_pivot = emo_platform.pivot(index="creative_emotion", columns="platform",
                                values="conversion_rate").fillna(0)
fig8 = go.Figure(data=go.Heatmap(
    z=emo_pivot.values,
    x=emo_pivot.columns.tolist(),
    y=emo_pivot.index.tolist(),
    colorscale="RdYlGn",
    text=np.round(emo_pivot.values, 2),
    texttemplate="%{text}%",
    colorbar=dict(title="Conv. Rate (%)")
))
fig8.update_layout(template="plotly_white", xaxis_title="Plataforma",
                   yaxis_title="Emoção Criativa")
st.plotly_chart(fig8, use_container_width=True)

st.divider()

# Gráfico 9 – Taxa de Conversão por Dispositivo e Plataforma
st.subheader("📱 Taxa de Conversão por Dispositivo e Plataforma")
st.caption("Comparação entre dispositivos dentro de cada plataforma")
device_platform = (filtered_df.groupby(["platform", "device_type"], observed=True)["conversion_rate"]
                   .mean().reset_index())
fig9 = px.bar(device_platform, x="platform", y="conversion_rate",
              color="device_type", barmode="group",
              labels={"platform": "Plataforma", "conversion_rate": "Taxa de Conversão Média (%)",
                      "device_type": "Dispositivo"},
              color_discrete_sequence=px.colors.qualitative.Pastel)
fig9.update_layout(template="plotly_white")
st.plotly_chart(fig9, use_container_width=True)

st.divider()

# Gráfico 10 – Impacto do CTA na Taxa de Conversão
st.subheader("📣 Impacto do Call-to-Action na Taxa de Conversão")
st.caption("Comparação da taxa de conversão média em anúncios com e sem CTA, por plataforma")
cta_effect = (filtered_df.groupby(["platform", "has_call_to_action"], observed=True)["conversion_rate"]
              .mean().reset_index())
cta_effect["CTA"] = cta_effect["has_call_to_action"].map({1: "Com CTA", 0: "Sem CTA"})
fig10 = px.bar(cta_effect, x="platform", y="conversion_rate",
               color="CTA", barmode="group",
               labels={"platform": "Plataforma", "conversion_rate": "Taxa de Conversão Média (%)", "CTA": ""},
               color_discrete_map={"Com CTA": "#01696f", "Sem CTA": "#bab9b4"})
fig10.update_layout(template="plotly_white")
st.plotly_chart(fig10, use_container_width=True)

st.divider()

# Gráfico 11 – Evolução Temporal da Taxa de Conversão por Plataforma
st.subheader("📅 Evolução Temporal da Taxa de Conversão por Plataforma")
st.caption("Tendência mensal da taxa de conversão média por plataforma")
filtered_df["month"] = filtered_df["start_date"].dt.to_period("M").dt.to_timestamp()
time_platform = (filtered_df.groupby(["month", "platform"], observed=True)["conversion_rate"]
                 .mean().reset_index())
fig11 = px.line(time_platform, x="month", y="conversion_rate", color="platform", markers=True,
                labels={"month": "Mês", "conversion_rate": "Taxa de Conversão Média (%)",
                        "platform": "Plataforma"},
                color_discrete_sequence=px.colors.qualitative.Set2)
fig11.update_layout(template="plotly_white")
st.plotly_chart(fig11, use_container_width=True)

st.divider()

# Gráfico 12 – Matriz de Correlação entre Métricas
st.subheader("🔗 Matriz de Correlação entre Métricas")
st.caption("Correlação de Pearson entre as principais métricas numéricas")
corr_cols = ["impressions", "clicks", "conversions", "CTR", "CPC", "conversion_rate", "CPA", "creative_age_days"]
corr_matrix = filtered_df[corr_cols].corr().round(2)
fig12 = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns.tolist(),
    y=corr_matrix.index.tolist(),
    colorscale="RdBu",
    zmid=0,
    text=corr_matrix.values,
    texttemplate="%{text}",
    colorbar=dict(title="Pearson r")
))
fig12.update_layout(template="plotly_white")
st.plotly_chart(fig12, use_container_width=True)

st.divider()

# --------------------------------------------------
# Tabela – Top Formatos de Anúncio por Conversões
# --------------------------------------------------
st.subheader("🏆 Top Formatos de Anúncio por Conversões")
top_formats = (
    filtered_df
    .groupby("creative_format", observed=True)[["conversions", "CTR", "conversion_rate", "CPA"]]
    .agg({"conversions": "sum", "CTR": "mean", "conversion_rate": "mean", "CPA": "mean"})
    .sort_values("conversions", ascending=False)
    .reset_index()
    .rename(columns={
        "creative_format":  "Formato",
        "conversions":      "Total Conversões",
        "CTR":              "CTR Médio (%)",
        "conversion_rate":  "Taxa Conv. Média (%)",
        "CPA":              "CPA Médio ($)"
    })
)
st.dataframe(top_formats, use_container_width=True)

# --------------------------------------------------
# Rodapé
# --------------------------------------------------
st.caption("Dados: tech_advertising_campaigns_dataset_filtered.csv | Segmento: Mulheres 45-54 | Lead Generation")
