import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime

# Configuração de Layout - Estilo Profissional Claro
st.set_page_config(page_title="IA ELITE 2026", layout="wide", page_icon="📈")

# CSS para Interface Elegante e Legível
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #1e1e1e; }
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div[data-testid="stExpander"] { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; }
    .stButton>button { background-color: #007bff; color: white; font-weight: bold; border-radius: 8px; height: 3em; }
    h1, h2, h3 { color: #0d47a1; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

# --- LÓGICA DE PREVISÃO ---
def analise_pro_2026(df, casa, fora):
    # Médias dos últimos 10 jogos (Fase Atual 2026)
    df_recent = df.tail(150) # Pega os jogos mais frescos da temporada
    avg_gols_liga = df_recent['FTHG'].mean() + df_recent['FTAG'].mean()
    
    # Força Ofensiva e Defensiva
    casa_gols_pro = df[df['HomeTeam'] == casa]['FTHG'].tail(8).mean()
    casa_gols_contra = df[df['HomeTeam'] == casa]['FTAG'].tail(8).mean()
    fora_gols_pro = df[df['AwayTeam'] == fora]['FTAG'].tail(8).mean()
    fora_gols_contra = df[df['AwayTeam'] == fora]['FTHG'].tail(8).mean()

    # Lambda (Poisson)
    l_casa = (casa_gols_pro + fora_gols_contra) / 2
    l_fora = (fora_gols_pro + casa_gols_contra) / 2
    
    return l_casa, l_fora

# --- INTERFACE ---
st.title("📈 IA Elite Predictor: Terminal 2026")
st.subheader(f"📅 Data de Operação: {datetime.now().strftime('%d/%m/%Y')}")

# Seletor de Ligas - Conectado com as bases reais 25/26
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
    
    # Seleção de Confronto
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Time Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Time Visitante", times, index=min(1, len(times)-1))

    # Processamento
    l_c, l_f = analise_pro_2026(df, t_casa, t_fora)
    
    # Probabilidades Poisson
    p_c = p_e = p_f = o25 = 0
    for i in range(10):
        for j in range(10):
            prob = poisson.pmf(i, l_c) * poisson.pmf(j, l_f)
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            if (i+j) > 2.5: o25 += prob

    # --- DASHBOARD VISUAL ---
    st.write("### 📊 Probabilidades Calculadas (IA)")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    col_b.metric("Empate", f"{p_e:.1%}")
    col_c.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    col_d.metric("Over 2.5 Gols", f"{o25:.1%}")

    st.markdown("---")
    
    # --- ÁREA DE ODDS E VALOR (EV+) ---
    st.write("### 💰 Filtro de Valor e Gestão")
    v1, v2, v3 = st.columns(3)
    
    with v1:
        odd_c = st.number_input(f"Odd {t_casa}", value=2.0)
        ev_c = (p_c * odd_c) - 1
        st.write(f"**EV {t_casa}:** {ev_c:+.2f}")
        if ev_c > 0: st.success("💎 VALOR ENCONTRADO")
        else: st.error("Sem Valor")

    with v2:
        odd_o = st.number_input("Odd Over 2.5", value=1.95)
        ev_o = (o25 * odd_o) - 1
        st.write(f"**EV Over:** {ev_o:+.2f}")
        if ev_o > 0: st.success("💎 VALOR ENCONTRADO")
        else: st.error("Sem Valor")

    with v3:
        # Escanteios Estimados por Pressão Ofensiva (Regra 2026)
        proj_cantos = (l_c * 3.8) + (l_f * 3.2)
        st.metric("⛳ Projeção de Escanteios", f"{proj_cantos:.1f}")
        st.caption(f"Prob. Over 9.5: **{min(99.0, (proj_cantos*9.5)):.1%}%**")

    # --- PLACAR E MINUTAGEM ---
    st.markdown("---")
    st.write("### ⏱️ Mapa de Calor de Gols (Probabilidade por Tempo)")
    
    # Simulação de minutagem baseada em gols médios
    m1, m2 = st.columns(2)
    with m1:
        st.write("**⚽ Primeiro Tempo (HT)**")
        st.progress(int(o25 * 35)) # Estimativa visual
        st.write(f"Chance de Gol no HT: **{(o25 * 0.7):.1%}**")
    with m2:
        st.write("**⚽ Segundo Tempo (FT)**")
        st.progress(int(o25 * 65))
        st.write(f"Chance de Gol no FT: **{(o25 * 0.9):.1%}**")

else:
    st.error("Não foi possível carregar os dados de 2026. Verifique se a temporada já iniciou.")
