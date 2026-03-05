import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime

st.set_page_config(page_title="Terminal IA - Jogos do Dia", layout="wide", page_icon="⚽")

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        # Converter coluna de data para o formato datetime do Python
        for fmt in ('%d/%m/%y', '%d/%m/%Y'):
            try:
                df['Date'] = pd.to_datetime(df['Date'], format=fmt)
                break
            except: continue
        return df
    except: return None

def calcular_poisson(m_casa, m_fora):
    prob_c = prob_e = prob_f = prob_o25 = prob_btts = 0
    for i in range(10):
        for j in range(10):
            p = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: prob_c += p
            elif i == j: prob_e += p
            else: prob_f += p
            if (i + j) > 2.5: prob_o25 += p
            if i > 0 and j > 0: prob_btts += p
    return prob_c, prob_e, prob_f, prob_o25, prob_btts

st.title("⚽ Scanner de Valor - Jogos do Dia")

# --- SIDEBAR CONFIG ---
st.sidebar.header("🏆 Filtros de Mercado")
liga = st.sidebar.selectbox("Liga", ["Brasil Serie A", "Premier League", "La Liga", "Serie A (ITA)", "Bundesliga"])
temp = st.sidebar.selectbox("Temporada", ["2026 (ou Atual)", "2025"])

mapas = {
    "Brasil Serie A": "BRA.csv", "Premier League": "E0.csv", 
    "La Liga": "SP1.csv", "Serie A (ITA)": "I1.csv", "Bundesliga": "D1.csv"
}
cod_temp = "2526" if temp == "2026 (ou Atual)" else "2425"
url = f"https://www.football-data.co.uk/mmz4281/{cod_temp}/{mapas[liga]}"

df = load_data(url)

if df is not None:
    # Pegar a data mais recente no arquivo (simulando "hoje")
    data_maxima = df['Date'].max()
    st.info(f"📅 Exibindo jogos da rodada de: {data_maxima.strftime('%d/%m/%Y')}")
    
    # Filtrar jogos dessa data específica
    jogos_hoje = df[df['Date'] == data_maxima]
    
    # Gestão de Banca na Sidebar
    st.sidebar.divider()
    banca = st.sidebar.number_input("Sua Banca (R$)", value=1000.0)
    kelly_agg = st.sidebar.slider("Critério Kelly %", 1, 100, 20) / 100

    # --- GRID DE JOGOS ---
    for idx, jogo in jogos_hoje.iterrows():
        casa = jogo['HomeTeam']
        fora = jogo['AwayTeam']
        
        # Cálculo de Médias (Baseado no histórico total da temporada carregada)
        m_c = df[df['HomeTeam'] == casa]['FTHG'].mean()
        m_f = df[df['AwayTeam'] == fora]['FTAG'].mean()
        
        p_c, p_e, p_f, p_o, p_b = calcular_poisson(m_c, m_f)
        
        with st.expander(f"🏟️ {casa} vs {fora} | Analisar Odds"):
            col1, col2, col3 = st.columns(3)
            
            # Inputs de Odds
            with col1:
                odd_c = st.number_input(f"Odd {casa}", value=2.0, key=f"c_{idx}")
                ev_c = (p_c * odd_c) - 1
                st.metric("Prob Casa", f"{p_c:.1%}", f"{ev_c:.1%} EV")
                
            with col2:
                odd_e = st.number_input(f"Odd Empate", value=3.0, key=f"e_{idx}")
                ev_e = (p_e * odd_e) - 1
                st.metric("Prob Empate", f"{p_e:.1%}", f"{ev_e:.1%} EV")
                
            with col3:
                odd_f = st.number_input(f"Odd {fora}", value=3.5, key=f"f_{idx}")
                ev_f = (p_f * odd_f) - 1
                st.metric("Prob Fora", f"{p_f:.1%}", f"{ev_f:.1%} EV")
            
            # Sugestão de Stake (Kelly)
            if ev_c > 0:
                f_kelly = ((p_c * (odd_c - 1)) - (1 - p_c)) / (odd_c - 1)
                st.success(f"💎 VALOR ENCONTRADO EM {casa.upper()}! Apostar: R$ {f_kelly * banca * kelly_agg:.2f}")
            elif ev_f > 0:
                f_kelly = ((p_f * (odd_f - 1)) - (1 - p_f)) / (odd_f - 1)
                st.success(f"💎 VALOR ENCONTRADO EM {fora.upper()}! Apostar: R$ {f_kelly * banca * kelly_agg:.2f}")
            else:
                st.write("⚠️ Sem valor matemático nas odds informadas.")

else:
    st.error("❌ Não foi possível carregar os jogos desta liga/temporada.")