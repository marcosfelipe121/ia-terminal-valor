import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Design Profissional
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; }
    .explainer { background-color: #ffffff; padding: 10px; border-radius: 5px; border-left: 5px solid #1e3a8a; font-size: 0.9em; margin-bottom: 10px; }
    .player-card { background-color: #fff3e0; padding: 15px; border-radius: 10px; border: 1px solid #ffb74d; }
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
    gols_con = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time:
            gols_pro += row['FTHG']; gols_con += row['FTAG']
        else:
            gols_pro += row['FTAG']; gols_con += row['FTHG']
    return (gols_pro / 8), (gols_con / 8), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite: Scout Detalhado v14")

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
    col1, col2 = st.columns(2)
    with col1: t_casa = st.selectbox("🏠 Mandante", times)
    with col2: t_fora = st.selectbox("🏃 Visitante", times, index=min(1, len(times)-1))

    m_c_pro, m_c_con, hist_casa = get_stats(df, t_casa)
    m_f_pro, m_f_con, hist_fora = get_stats(df, t_fora)

    # --- MÉTRICAS GERAIS ---
    st.write("---")
    o15 = 0
    for i in range(10):
        for j in range(10):
            if (i+j) > 1.5: o15 += poisson.pmf(i, m_c_pro) * poisson.pmf(j, m_f_pro)
    
    st.subheader("📊 Explicação da Estimativa de Scout")
    st.markdown(f"""
    <div class='explainer'>
    <b>Como calculamos:</b><br>
    • <b>Faltas:</b> Baseado na média de gols sofridos (Exposição defensiva).<br>
    • <b>Roubadas:</b> Baseado no volume de gols do adversário (Necessidade de desarme).
    </div>
    """, unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.metric(f"Faltas Est. {t_casa}", f"{m_c_con * 8.8:.1f}", help="Cálculo: Média Gols Sofridos x 8.8")
        st.metric(f"Desarmes Est. {t_casa}", f"{m_f_pro * 11.5:.1f}", help="Cálculo: Média Gols Pró Adversário x 11.5")
    with s2:
        st.metric(f"Faltas Est. {t_fora}", f"{m_f_con * 9.2:.1f}")
        st.metric(f"Desarmes Est. {t_fora}", f"{m_c_pro * 11.2:.1f}")

    # --- PLAYER PROPS ESTIMATOR ---
    st.write("---")
    st.subheader("👤 Estimador de Scout por Jogador (Beta)")
    st.write("Selecione o perfil do jogador que você quer analisar para este jogo:")
    
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        perfil = st.selectbox("Perfil do Jogador", ["Volante Pegador", "Zagueiro Físico", "Lateral Ofensivo", "Atacante Alvo"])
    with p_col2:
        nivel = st.select_slider("Nível de Agressividade", options=["Baixo", "Médio", "Alto"])
    
    # Lógica de Estimativa Individual
    base_faltas = 1.2 if nivel == "Baixo" else (2.1 if nivel == "Médio" else 3.4)
    if perfil == "Volante Pegador":
        est_f = base_faltas * (1 + m_c_con/2)
        est_d = 2.5 * (1 + m_f_pro/2)
    elif perfil == "Zagueiro Físico":
        est_f = (base_faltas * 0.8) * (1 + m_c_con/2)
        est_d = 1.8 * (1 + m_f_pro/2)
    else:
        est_f = 0.8; est_d = 1.0

    with p_col3:
        st.markdown(f"""
        <div class='player-card'>
        <b>Projeção p/ o Jogador:</b><br>
        🔥 Faltas: <b>{est_f:.2f}</b><br>
        🛡️ Desarmes: <b>{est_d:.2f}</b>
        </div>
        """, unsafe_allow_html=True)

    # --- REGISTRO ---
    st.write("---")
    st.subheader("📋 Registro de Dados")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
    hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
    st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.error("Erro na base. Clique em 'Forçar Atualização'.")
