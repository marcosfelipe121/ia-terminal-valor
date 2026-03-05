import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Design Profissional (Clean White)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .stDataFrame { background-color: #ffffff; border-radius: 10px; }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # Tenta converter a data de forma segura
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

def get_stats(df, time):
    # Puxa os últimos 8 jogos do time (como mandante ou visitante)
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    gols_pro = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time: gols_pro += row['FTHG']
        else: gols_pro += row['FTAG']
    return (gols_pro / 8 if len(recent) > 0 else 0), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite Predictor")
st.caption(f"Status: Sincronizado com Bases de Dados Reais 2025/2026")

liga = st.sidebar.selectbox("🏆 Selecione a Liga", ["Premier League (ING)", "La Liga (ESP)", "Serie A (ITA)", "Série A (BRA)"])
url_map = {
    "Premier League (ING)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "La Liga (ESP)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Serie A (ITA)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Série A (BRA)": "https://www.football-data.co.uk/mmz4281/2526/BRA.csv"
}

df = load_data(url_map[liga])

if df is not None:
    times = sorted(df['HomeTeam'].unique())
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Time Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Time Visitante", times, index=min(1, len(times)-1))

    # Cálculos Médias e Histórico
    m_casa, hist_casa = get_stats(df, t_casa)
    m_fora, hist_fora = get_stats(df, t_fora)
    
    # Probabilidades Poisson
    p_c = p_e = p_f = o25 = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: p_c += prob
            elif i == j: p_e += prob
