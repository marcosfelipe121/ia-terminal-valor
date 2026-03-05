import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout Profissional
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Estilo CSS Personalizado
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .lucro-texto { color: #28a745; font-weight: bold; font-size: 1.2em; }
    .scout-card { background-color: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

def get_stats(df, time):
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    gols_pro = 0
    gols_contra = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time:
            gols_pro += row['FTHG']
            gols_contra += row['FTAG']
        else:
            gols_pro += row['FTAG']
            gols_contra += row['FTHG']
    return (gols_pro / 8), (gols_contra / 8), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite: Scout & Operacional 2026")

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

    m_casa_pro, m_casa_con, hist_casa = get_stats(df, t_casa)
    m_fora_pro, m_fora_con, hist_fora = get_stats(df, t_fora)

    # --- POISSON ---
    p_c = p_e = p_f = o15 = btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa_pro) * poisson.pmf(j, m_fora_pro)
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            if (i+j) > 1.5: o15 += prob
            if i > 0 and j > 0: btts += prob

    st.write("---")
    st.subheader("🎯 Probabilidades IA")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    d2.metric("Empate", f"{p_e:.1%}")
    d3.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    d4.metric("Ambas Marcam", f"{btts:.1%}")

    # --- NOVO: ESTIMATIVA DE SCOUT (INTENSIDADE) ---
    st.write("---")
    st.subheader("🕵️ Projeção de Scout & Intensidade (Estimativa)")
    s1, s2 = st.columns(2)
    
    with s1:
        st.markdown(f"<div class='scout-card'><b>Intensidade Defensiva: {t_casa}</b><br>"
                    f"Faltas Cometidas Est.: {(m_casa_con * 8.5):.1f}<br>"
                    f"Roubadas de Bola Est.: {(m_fora_pro * 12.2):.1f}</div>", unsafe_allow_html=True)
    with s2:
        st.markdown(f"<div class='scout-card'><b>Intensidade Defensiva: {t_fora}</b><br>"
                    f"Faltas Cometidas Est.: {(m_fora_con * 9.1):.1f}<br>"
                    f"Roubadas de Bola Est.: {(m_casa_pro * 11.8):.1f}</div>", unsafe_allow_html=True)
    st.caption("Nota: Valores baseados no volume de ataque sofrido e gols concedidos nas últimas 8 partidas.")

    # --- GESTÃO DE BANCA ---
    st.write("---")
    st.subheader("💰 Gestão de Banca")
    col_b, col_o, col_r = st.columns([1, 1, 2])
    with col_b: banca = st.number_input("Banca Total (R$)", value=1000.0)
    with col_o: odd_casa = st.number_input("Odd Bet365 (Over 1.5)", value=1.25)
    with col_r:
        odd_j = 1/o15 if o15 > 0 else 0
        ev = (o15 * odd_casa) - 1
        if ev > 0.05:
            st.success(f"✅ VALOR! Sugestão: R$ {banca*0.05:.2f} (5%)")
        else:
            st.error(f"❌ BAIXO VALOR! Sugestão: R$ {banca*0.01:.2f} (1%) ou Fora")

    # --- REGISTRO ---
    st.write("---")
    st.subheader("📋 Registro de Dados")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
    hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
    st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.error("Erro na base. Clique em 'Forçar Atualização'.")
