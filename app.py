import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Estilo Profissional Clean
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
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
st.title("🛡️ Terminal IA Elite: Multi-Mercados")

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

    # --- CONFIGURAÇÃO DE LINHAS ---
    st.write("---")
    st.subheader("⚙️ Configurar Linhas da Casa")
    col_config1, col_config2 = st.columns(2)
    with col_config1:
        linha_g = st.selectbox("Linha de Gols", [0.5, 1.5, 2.5, 3.5], index=1) # Padrão em 1.5
    with col_config2:
        linha_c = st.selectbox("Linha de Cantos", [7.5, 8.5, 9.5, 10.5], index=2)

    # Cálculo Poisson Avançado
    p_c = p_e = p_f = prob_g_linha = prob_btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            # Resultado Final
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            # Linha de Gols
            if (i+j) > linha_g: prob_g_linha += prob
            # Ambas Marcam (BTTS)
            if i > 0 and j > 0: prob_btts += prob

    # --- RESULTADOS PRINCIPAIS ---
    st.write("---")
    res1, res2, res3, res4 = st.columns(4)
    res1.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    res2.metric("Empate", f"{p_e:.1%}")
    res3.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    res4.metric(f"Ambas Marcam (Sim)", f"{prob_btts:.1%}")

    # --- ANÁLISE DE VALOR ---
    st.write("---")
    st.subheader("💰 Filtro de Valor Esperado (EV+)")
    v1, v2, v3 = st.columns(3)
    
    with v1:
        odd_g = st.number_input(f"Odd Over {linha_g}", value=1.40)
        ev_g = (prob_g_linha * odd_g) - 1
        st.write(f"Prob. Over {linha_g}: **{prob_g_linha:.1%}%**")
        if ev_g > 0: st.success(f"💎 VALOR OVER {linha_g}")
        else: st.error("Sem Valor")

    with v2:
        odd_btts = st.number_input(f"Odd Ambas Marcam", value=1.85)
        ev_b = (prob_btts * odd_btts) - 1
        if ev_b > 0: st.success(f"💎 VALOR BTTS")
        else: st.error("Sem Valor")

    with v3:
        # Projeção de Cantos Dinâmica
        proj_c = (m_casa * 3.5) + (m_fora * 3.0)
        st.metric("⛳ Cantos Projetados", f"{proj_c:.1f}")
        st.caption(f"Prob. Over {linha_c}: **{(proj_c / (linha_c + 4.5)):.1%}%**")

    # --- HISTÓRICO ---
    st.write("---")
    st.subheader("📋 Registro de Dados (Últimas 8 Partidas)")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    st.dataframe(hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True)

else:
    st.warning("⚠️ Aguardando dados... Se travar, clique em 'Forçar Atualização'.")
