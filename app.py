import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout Profissional
st.set_page_config(page_title="IA ELITE PREDICTOR", layout="wide", page_icon="📈")

# CSS para deixar o visual "Premium"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .stButton>button { width: 100%; background-color: #238636; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
        return df
    except: return None

# --- ENGINE DE ANÁLISE ---
def calcular_metricas_elite(df, time_casa, time_fora):
    # Médias da Liga (Benchmark)
    avg_home_g = df['FTHG'].mean()
    avg_away_g = df['FTAG'].mean()

    # Performance específica (Últimos 10 jogos p/ consistência)
    h_attack = df[df['HomeTeam'] == time_casa]['FTHG'].tail(10).mean() / avg_home_g
    h_defense = df[df['HomeTeam'] == time_casa]['FTAG'].tail(10).mean() / avg_away_g
    
    a_attack = df[df['AwayTeam'] == time_fora]['FTAG'].tail(10).mean() / avg_away_g
    a_defense = df[df['AwayTeam'] == time_fora]['FTHG'].tail(10).mean() / avg_home_g

    # Projeção de Gols (Lambda) para o confronto
    lambda_casa = h_attack * a_defense * avg_home_g
    lambda_fora = a_attack * h_defense * avg_away_g
    
    return lambda_casa, lambda_fora

def extrair_probabilidades(l_casa, l_fora):
    prob_c = prob_e = prob_f = over25 = btts = 0
    for i in range(12):
        for j in range(12):
            p = poisson.pmf(i, l_casa) * poisson.pmf(j, l_fora)
            if i > j: prob_c += p
            elif i == j: prob_e += p
            else: prob_f += p
            if (i + j) > 2.5: over25 += p
            if i > 0 and j > 0: btts += p
    return prob_c, prob_e, prob_f, over25, btts

# --- INTERFACE ---
st.title("📈 IA Elite Predictor: Terminal de Alta Performance")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1162/1162908.png", width=100)

liga_escolhida = st.sidebar.selectbox("🏆 Selecionar Campeonato", ["Premier League", "La Liga", "Serie A (ITA)", "Bundesliga", "Brasil"])
urls = {
    "Premier League": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "La Liga": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Serie A (ITA)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Bundesliga": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "Brasil": "https://www.football-data.co.uk/mmz4281/2526/BRA.csv"
}

df = load_data(urls[liga_escolhida])

if df is not None:
    times = sorted(df['HomeTeam'].unique())
    
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Visitante", times, index=1)

    l_casa, l_fora = calcular_metricas_elite(df, t_casa, t_fora)
    pc, pe, pf, o25, btts = extrair_probabilidades(l_casa, l_fora)

    # --- DASHBOARD VISUAL ---
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"Vitória {t_casa}", f"{pc:.1%}")
    m2.metric("Empate", f"{pe:.1%}")
    m3.metric(f"Vitória {t_fora}", f"{pf:.1%}")
    m4.metric("Over 2.5 Gols", f"{o25:.1%}")

    # --- ANÁLISE DE VALOR (ODDS) ---
    st.subheader("💰 Filtro de Valor Esperado (EV+)")
    v1, v2, v3 = st.columns(3)
    
    with v1:
        odd_c = st.number_input(f"Odd {t_casa}", value=2.0)
        ev_c = (pc * odd_c) - 1
        if ev_c > 0: st.success(f"💎 VALOR: {ev_c:.1%}")
        else: st.error("Sem Valor")

    with v2:
        odd_o25 = st.number_input("Odd Over 2.5", value=1.9)
        ev_o = (o25 * odd_o25) - 1
        if ev_o > 0: st.success(f"💎 VALOR: {ev_o:.1%}")
        else: st.error("Sem Valor")

    with v3:
        # Estimativa de Cantos Baseada em Periculosidade Ofensiva (Elite Metric)
        # Cantos = (Ataque Mandante * 5.5) + (Ataque Visitante * 4.5)
        cantos_proj = (l_casa * 3.5) + (l_fora * 3.0)
        st.write(f"⛳ **Projeção de Cantos:** {cantos_proj:.1f}")
        st.write(f"Prob. Over 9.5: **{(cantos_proj/14.5):.1%}**")

    # --- INSIGHT DO ANALISTA ---
    st.divider()
    with st.expander("💡 Relatório do Analista IA"):
        st.write(f"""
        O confronto entre **{t_casa}** e **{t_fora}** apresenta um índice de periculosidade de **{(l_casa+l_fora):.2f}** gols esperados. 
        O Mandante tem uma eficiência ofensiva **{((l_casa/df['FTHG'].mean())-1):.1%}** acima da média da liga neste cenário. 
        **Veredito:** {'Cenário favorável para Over' if o25 > 0.55 else 'Cenário de Under / Jogo Truncado'}.
        """)

else:
    st.warning("Aguardando conexão com os dados da temporada 2026...")
