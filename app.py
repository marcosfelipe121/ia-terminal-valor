import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout Profissional
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Design Profissional (Clean White com Cards)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .stDataFrame { background-color: #ffffff; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        # Limpeza de data para exibir apenas DD/MM/AAAA
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

def get_stats(df, time):
    # Puxa os últimos 8 jogos para análise de tendência
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    gols_pro = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time: gols_pro += row['FTHG']
        else: gols_pro += row['FTAG']
    return (gols_pro / 8 if len(recent) > 0 else 0), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite Predictor Pro")
st.caption("Sincronizado: Temporada 2025/2026 | Dados Oficiais Football-Data")

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

df = load_data(url_map[liga])

if df is not None and not df.empty:
    times = sorted(df['HomeTeam'].unique())
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Visitante", times, index=min(1, len(times)-1))

    m_casa, hist_casa = get_stats(df, t_casa)
    m_fora, hist_fora = get_stats(df, t_fora)

    # --- CÁLCULOS POISSON ---
    p_c = p_e = p_f = o15 = o25 = btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            if (i+j) > 1.5: o15 += prob
            if (i+j) > 2.5: o25 += prob
            if i > 0 and j > 0: btts += prob

    # --- DASHBOARD DE MÉTRICAS ---
    st.write("---")
    st.subheader("🎯 Probabilidades Calculadas pela IA")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    d2.metric("Empate", f"{p_e:.1%}")
    d3.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    d4.metric("Ambas Marcam", f"{btts:.1%}")

    # --- ANÁLISE DE VALOR (O SEU CAMPO DE AJUSTE) ---
    st.write("---")
    st.subheader("💰 Análise de Valor (Preencha as Odds da Bet365)")
    v1, v2 = st.columns(2)
    
    with v1:
        st.markdown(f"**Mercado: Over 1.5 Gols**")
        odd_casa_g = st.number_input(f"Odd da Bet365 para Over 1.5", value=1.25, step=0.01, key="g")
        odd_justa_g = 1 / o15 if o15 > 0 else 0
        ev_g = (o15 * odd_casa_g) - 1
        st.write(f"📈 Probabilidade IA: **{o15:.1%}** | ⚖️ Odd Justa: **{odd_justa_g:.2f}**")
        if ev_g > 0: st.success(f"💎 VALOR ENCONTRADO! (+{ev_g:.1%})")
        else: st.error(f"❌ SEM VALOR (A odd mínima deveria ser {odd_justa_g:.2f})")

    with v2:
        st.markdown(f"**Mercado: Ambas Marcam (Sim)**")
        odd_casa_b = st.number_input(f"Odd da Bet365 para BTTS", value=1.80, step=0.01, key="b")
        odd_justa_b = 1 / btts if btts > 0 else 0
        ev_b = (btts * odd_casa_b) - 1
        st.write(f"📈 Probabilidade IA: **{btts:.1%}** | ⚖️ Odd Justa: **{odd_justa_b:.2f}**")
        if ev_b > 0: st.success(f"💎 VALOR ENCONTRADO! (+{ev_b:.1%})")
        else: st.error(f"❌ SEM VALOR (A odd mínima deveria ser {odd_justa_b:.2f})")

    # --- MAPA DE TEMPO E CANTOS ---
    st.write("---")
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("⛳ Escanteios & Tempo")
        proj_c = (m_casa * 3.5) + (m_fora * 3.0)
        st.metric("Projeção de Cantos", f"{proj_c:.1f}")
        st.write("Tendência de Gols (1º Tempo)")
        st.progress(min(100, int((o15 * 0.4) * 100)))
        st.write("Tendência de Gols (2º Tempo)")
        st.progress(min(100, int((o15 * 0.6) * 100)))

    with col_p2:
        st.subheader("📋 Registro de Jogos (Dados Reais)")
        hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
        hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
        hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
        st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar dados. Tente 'Forçar Atualização' na lateral.")
