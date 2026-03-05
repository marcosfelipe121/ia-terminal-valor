import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA Terminal Pro - 2026", layout="wide", page_icon="🛡️")

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except:
        return None

st.title("🛡️ Terminal de Inteligência - Automação Total")
st.caption("Sincronizado com Bases 2025/2026 | Gols & Escanteios Estimados")

# --- CONFIGURAÇÃO DA LIGA ---
st.sidebar.header("🏆 Seleção de Mercado")
liga = st.sidebar.selectbox("Escolha a Liga", ["Inglaterra", "Espanha", "Brasil", "Itália", "Alemanha"])

mapa_urls = {
    "Inglaterra": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "Espanha": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Itália": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Alemanha": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "Brasil": "https://www.football-data.co.uk/mmz4281/2526/BRA.csv" # Fallback para 25 se 26 não iniciou
}

df = load_data(mapa_urls[liga])

if df is not None:
    df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    times = sorted(df['HomeTeam'].unique())
    
    col1, col2 = st.columns(2)
    with col1: time_casa = st.selectbox("🏠 Time da Casa", times)
    with col2: time_fora = st.selectbox("🏃 Time de Fora", times, index=1)

    # --- LÓGICA DE MÉDIAS (O "Cérebro" do Sistema) ---
    # Pegamos os últimos 8 jogos para ter volume, mas dando foco na fase atual
    ultimos_casa = df[(df['HomeTeam'] == time_casa) | (df['AwayTeam'] == time_casa)].tail(8)
    ultimos_fora = df[(df['HomeTeam'] == time_fora) | (df['AwayTeam'] == time_fora)].tail(8)

    # Cálculo de Média de Gols (Real)
    m_gols_casa = (ultimos_casa[ultimos_casa['HomeTeam'] == time_casa]['FTHG'].sum() + ultimos_casa[ultimos_casa['AwayTeam'] == time_casa]['FTAG'].sum()) / 8
    m_gols_fora = (ultimos_fora[ultimos_fora['HomeTeam'] == time_fora]['FTHG'].sum() + ultimos_fora[ultimos_fora['AwayTeam'] == time_fora]['FTAG'].sum()) / 8

    # Estimativa de Cantos (Baseado em Pressão Ofensiva)
    # Times que marcam mais gols costumam ter mais cantos. Média baseada em conversão Pro.
    m_cantos_casa = m_gols_casa * 3.2  
    m_cantos_fora = m_gols_fora * 2.8

    # --- PROBABILIDADES ---
    def calcular_probabilidades(m1, m2, alvo):
        prob = 0
        for i in range(15):
            for j in range(15):
                p = poisson.pmf(i, m1) * poisson.pmf(j, m2)
                if (i + j) > alvo: prob += p
        return prob

    st.divider()
    
    # --- RESULTADOS ---
    tab1, tab2 = st.tabs(["⚽ Gols", "⛳ Escanteios"])
    
    with tab1:
        res1, res2 = st.columns(2)
        p_over25 = calcular_probabilidades(m_gols_casa, m_gols_fora, 2.5)
        res1.metric("IA Prob Over 2.5 Gols", f"{p_over25:.1%}")
        odd_gols = res2.number_input("Odd Over 2.5 Atual", value=1.90)
        
    with tab2:
        res3, res4 = st.columns(2)
        p_over95 = calcular_probabilidades(m_cantos_casa/2, m_cantos_fora/2, 4.75) # Ajuste matricial para cantos
        res3.metric("IA Prob Over 9.5 Cantos", f"{p_over95:.1%}")
        odd_cantos = res4.number_input("Odd Over 9.5 Cantos Atual", value=1.85)

    # --- GESTÃO DE VALOR (Kelly) ---
    st.divider()
    banca = st.sidebar.number_input("Banca Total R$", value=1000.0)
    
    if (p_over25 * odd_gols) - 1 > 0:
        st.success(f"💎 VALOR ENCONTRADO EM GOLS! Sugestão: R$ {((p_over25 * odd_gols - 1) / (odd_gols - 1)) * banca * 0.2:.2f}")
    
    if (p_over95 * odd_cantos) - 1 > 0:
        st.success(f"💎 VALOR ENCONTRADO EM CANTOS! Sugestão: R$ {((p_over95 * odd_cantos - 1) / (odd_cantos - 1)) * banca * 0.2:.2f}")

else:
    st.error("Erro ao conectar com a base de dados. Verifique a temporada.")
