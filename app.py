import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA OPERADOR ELITE", layout="wide", page_icon="💰")

# Estilo para facilitar a leitura rápida
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stNumberInput { border: 2px solid #0d47a1; border-radius: 5px; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; }
    h3 { color: #0d47a1; }
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
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time: gols_pro += row['FTHG']
        else: gols_pro += row['FTAG']
    return (gols_pro / 8 if len(recent) > 0 else 0), recent

# --- INTERFACE ---
st.title("💰 Terminal IA: Comparador de Valor Real")
st.write("Selecione o jogo e preencha a Odd da Bet365 abaixo para saber se vale a pena.")

liga = st.sidebar.selectbox("🏆 Escolha a Liga", ["Premier League (ING)", "La Liga (ESP)", "Serie A (ITA)", "Série A (BRA)"])
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

    m_casa, _ = get_stats(df, t_casa)
    m_fora, _ = get_stats(df, t_fora)

    # --- CÁLCULO DE PROBABILIDADE ---
    prob_over15 = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if (i+j) > 1.5: prob_over15 += prob

    st.divider()

    # --- CAMPO DE AJUSTE MANUAL (O QUE VOCÊ QUERIA) ---
    st.subheader("📝 Preencha os dados da Casa de Aposta")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        odd_bet365 = st.number_input("Quanto a Bet365 está pagando no Over 1.5?", value=1.25, step=0.01)
    
    # Cálculo da Odd Justa baseada na IA
    odd_justa = 1 / prob_over15 if prob_over15 > 0 else 0
    
    with col_input2:
        st.write(f"📈 **Probabilidade da IA para 2+ gols:** {prob_over15:.1%}")
        st.write(f"⚖️ **Odd Mínima Aceitável (Justa):** {odd_justa:.2f}")

    # --- VEREDITO FINAL ---
    st.divider()
    if odd_bet365 > odd_justa:
        st.success(f"💎 **VALOR ENCONTRADO!** A Odd de {odd_bet365} está acima do risco ({odd_justa:.2f}). **Pode apostar.**")
    else:
        st.error(f"❌ **NÃO APOSTE!** A Odd de {odd_bet365} está muito baixa. O risco não compensa o prêmio. A Odd mínima deveria ser {odd_justa:.2f}.")

    # --- PROJEÇÃO DE CANTOS ---
    st.divider()
    proj_c = (m_casa * 3.5) + (m_fora * 3.0)
    st.metric("⛳ Projeção de Escanteios para o Jogo", f"{proj_c:.1f}")

else:
    st.warning("Carregando base de dados 2026...")
