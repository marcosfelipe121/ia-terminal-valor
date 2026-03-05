import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Estilo Profissional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #0d47a1; font-family: 'Arial', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        # Converte e remove a hora
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

def get_stats(df, time):
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    gols_pro = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time: gols_pro += row['FTHG']
        else: gols_pro += row['FTAG']
    return (gols_pro / 8 if len(recent) > 0 else 0), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite Predictor")

if st.sidebar.button("♻️ Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()

liga = st.sidebar.selectbox("🏆 Liga", ["Premier League (ING)", "La Liga (ESP)", "Serie A (ITA)", "Série A (BRA)"])
url_map = {
    "Premier League (ING)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "La Liga (ESP)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Serie A (ITA)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Série A (BRA)": "https://www.football-data.co.uk/mmz4281/2526/BRA.csv"
}

df = load_data(url_map[liga])

if df is not None and not df.empty:
    times = sorted(df['HomeTeam'].unique())
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Visitante", times, index=min(1, len(times)-1))

    m_casa, hist_casa = get_stats(df, t_casa)
    m_fora, hist_fora = get_stats(df, t_fora)

    # --- CONFIGURAÇÃO ---
    st.write("---")
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        linha_g = st.selectbox("Linha de Gols (Over)", [0.5, 1.5, 2.5, 3.5], index=1)
    with col_config2:
        linha_c = st.selectbox("Linha de Cantos (Over)", [7.5, 8.5, 9.5, 10.5], index=2)

    # Cálculos
    p_c = p_e = p_f = prob_g_linha = prob_btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            if (i+j) > linha_g: prob_g_linha += prob
            if i > 0 and j > 0: prob_btts += prob

    # --- MÉTRICAS ---
    st.write("---")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    res2.metric("Empate", f"{p_e:.1%}")
    res3.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    res4.metric("Ambas Marcam", f"{prob_btts:.1%}")

    # --- VALOR ---
    st.write("---")
    st.subheader("💰 Análise de Valor (EV+)")
    v1, v2, v3 = st.columns(3)
    with v1:
        odd_g = st.number_input(f"Odd Over {linha_g}", value=1.40)
        ev_g = (prob_g_linha * odd_g) - 1
        st.write(f"Prob. Over {linha_g}: **{prob_g_linha:.1%}**")
        if ev_g > 0: st.success("💎 VALOR ENCONTRADO")
        else: st.error("Sem Valor")
    with v2:
        odd_btts = st.number_input(f"Odd BTTS (Sim)", value=1.80)
        ev_b = (prob_btts * odd_btts) - 1
        if ev_b > 0: st.success("💎 VALOR ENCONTRADO")
        else: st.error("Sem Valor")
    with v3:
        proj_c = (m_casa * 3.5) + (m_fora * 3.0)
        st.metric("⛳ Cantos Projetados", f"{proj_c:.1f}")
        st.caption(f"Prob. Over {linha_c}: **{(proj_c / (linha_c + 4.5)):.1%}**")

    # --- HISTÓRICO AJUSTADO ---
    st.write("---")
    st.subheader("📋 Registro de Jogos (Base de Dados)")
    
    # Preparação da tabela
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    
    # Renomeando colunas para o usuário
    hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
    hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
    
    # Exibição
    st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Sincronizando dados... Clique em 'Forçar Atualização' se demorar.")
