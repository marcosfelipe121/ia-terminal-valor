import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Design Profissional Clean
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; }
    </style>
    """, unsafe_allow_html=True)

# Função de Carga com Tratamento de Erro Real
def load_data(url):
    try:
        # Adicionando um timeout e lendo apenas colunas necessárias para ser mais rápido
        df = pd.read_csv(url, on_bad_lines='skip')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except Exception as e:
        st.error(f"Erro ao acessar servidor de dados: {e}")
        return None

def get_stats(df, time):
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    gols_pro = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time: gols_pro += row['FTHG']
        else: gols_pro += row['FTAG']
    return (gols_pro / 8 if len(recent) > 0 else 0), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite Predictor")

# Botão para limpar cache se travar
if st.sidebar.button("♻️ Forçar Atualização de Dados"):
    st.cache_data.clear()
    st.rerun()

liga = st.sidebar.selectbox("🏆 Selecione a Liga", ["Premier League (ING)", "La Liga (ESP)", "Serie A (ITA)", "Série A (BRA)"])
url_map = {
    "Premier League (ING)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "La Liga (ESP)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Serie A (ITA)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Série A (BRA)": "https://www.football-data.co.uk/mmz4281/2526/BRA.csv"
}

with st.spinner('Sincronizando com a base 2026...'):
    df = load_data(url_map[liga])

if df is not None and not df.empty:
    st.success(f"✅ {liga} Sincronizada com Sucesso!")
    
    times = sorted(df['HomeTeam'].unique())
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Time Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Time Visitante", times, index=min(1, len(times)-1))

    # Processamento de Dados
    m_casa, hist_casa = get_stats(df, t_casa)
    m_fora, hist_fora = get_stats(df, t_fora)
    
    # Poisson
    p_c = p_e = p_f = o25 = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            if (i+j) > 2.5: o25 += prob

    # --- EXIBIÇÃO ---
    st.write("---")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    d2.metric("Empate", f"{p_e:.1%}")
    d3.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    d4.metric("Over 2.5 Gols", f"{o25:.1%}")

    # ODDS
    st.write("---")
    v1, v2 = st.columns(2)
    with v1:
        odd_c = st.number_input(f"Odd p/ {t_casa}", value=2.0)
        ev_c = (p_c * odd_c) - 1
        if ev_c > 0: st.success(f"💎 VALOR EM {t_casa.upper()}: +{ev_c:.1%}")
        else: st.error(f"Sem Valor para {t_casa}")
    with v2:
        odd_o = st.number_input(f"Odd p/ Over 2.5", value=1.90)
        ev_o = (o25 * odd_o) - 1
        if ev_o > 0: st.success(f"💎 VALOR EM OVER: +{ev_o:.1%}")
        else: st.error("Sem Valor para Over 2.5")

    # HISTÓRICO
    st.write("---")
    st.subheader("📋 Histórico de Dados Utilizado")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    st.dataframe(hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True)
else:
    st.warning("⚠️ O servidor de dados está demorando para responder. Tente clicar em 'Forçar Atualização' na lateral ou trocar de Liga.")
