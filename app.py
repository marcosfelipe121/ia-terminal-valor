import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# 1. Configuração Inicial Segura
st.set_page_config(page_title="IA ELITE FIX", layout="wide")

@st.cache_data
def load_data_safe(url):
    try:
        df = pd.read_csv(url)
        # Limpeza básica: remove linhas vazias que o CSV do site costuma ter no final
        df = df.dropna(subset=['HomeTeam', 'AwayTeam'])
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com o servidor de dados: {e}")
        return pd.DataFrame()

# 2. URLs Oficiais (Temporada Atual)
url_map = {
    "Inglaterra (Premier)": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "Espanha (La Liga)": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "Alemanha (Bundesliga)": "https://www.football-data.co.uk/mmz4281/2425/D1.csv"
}

liga_sel = st.sidebar.selectbox("Escolha a Liga", list(url_map.keys()))
df = load_data_safe(url_map[liga_sel])

if not df.empty:
    # 3. Pegar os times DIRETAMENTE do arquivo (evita erro de digitação)
    lista_times = sorted(df['HomeTeam'].unique())
    
    col1, col2 = st.columns(2)
    with col1: t_casa = st.selectbox("Mandante", lista_times)
    with col2: t_fora = st.selectbox("Visitante", lista_times)

    # 4. Cálculo de Probabilidade Simples (Poisson)
    # Aqui filtramos os últimos 10 jogos de cada um
    df_casa = df[df['HomeTeam'] == t_casa].tail(10)
    df_fora = df[df['AwayTeam'] == t_fora].tail(10)
    
    if not df_casa.empty and not df_fora.empty:
        media_gols_casa = df_casa['FTHG'].mean()
        media_gols_fora = df_fora['FTAG'].mean()
        
        st.write(f"### Expectativa de Gols: {t_casa} ({media_gols_casa:.2f}) vs {t_fora} ({media_gols_fora:.2f})")
        
        # Cálculo de vitória (Poisson simplificado)
        prob_casa = poisson.pmf(range(6), media_gols_casa).sum() # Simplificação didática
        st.metric("Probabilidade de Vitória Casa", f"{prob_casa:.1%}")
    else:
        st.warning("Dados insuficientes para estes times nesta temporada.")
