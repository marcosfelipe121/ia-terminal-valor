import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout Profissional
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Estilo CSS para Interface Clean e Profissional
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .lucro-texto { color: #28a745; font-weight: bold; font-size: 1.2em; }
    .alerta-stake { background-color: #fff3cd; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; color: #856404; font-weight: bold; }
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

# --- TÍTULO E SIDEBAR ---
st.title("🛡️ Terminal IA Elite: Operacional & Risco")

if st.sidebar.button("♻️ Forçar Atualização"):
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

    # --- MOTOR DE PROBABILIDADES ---
    p_c = p_e = p_f = o15 = btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
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

    # --- NOVO: GESTÃO DE RISCO E STAKE REDUZIDA ---
    st.write("---")
    st.subheader("💰 Gestão de Banca & Entrada Recomendada")
    
    col_banca, col_odd, col_sugestao = st.columns([1, 1, 2])
    
    with col_banca:
        banca_total = st.number_input("Sua Banca Total (R$)", value=1000.0, step=100.0)
        unidade_padrao = banca_total * 0.05 # Sugere 5% como unidade cheia
    
    with col_odd:
        odd_atual = st.number_input("Odd Atual (Bet365)", value=1.25, step=0.01)
        odd_justa = 1 / o15 if o15 > 0 else 0

    with col_sugestao:
        ev = (o15 * odd_atual) - 1
        
        if ev > 0.15:
            st.success(f"🔥 **VALOR ALTO!** Entre com 1 Unidade Cheia: **R$ {unidade_padrao:.2f}**")
            st.write(f"Lucro Líquido Esperado: R$ {(unidade_padrao * (odd_atual - 1)):.2f}")
        elif ev > 0:
            stake_reduzida = unidade_padrao * 0.5
            st.warning(f"⚠️ **VALOR BAIXO / RISCO MÉDIO.** Entre com Meia Unidade: **R$ {stake_reduzida:.2f}**")
            st.write(f"Lucro Líquido Esperado: R$ {(stake_reduzida * (odd_atual - 1)):.2f}")
        else:
            st.error(f"❌ **SEM VALOR.** Não coloque seu dinheiro aqui. Aguarde a odd subir para {odd_justa:.2f}")

    # --- MAPA E REGISTRO ---
    st.write("---")
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("⛳ Escanteios & Tempo")
        proj_c = (m_casa * 3.5) + (m_fora * 3.0)
        st.metric("Projeção de Cantos", f"{proj_c:.1f}")
        
        p_ht = o15 * 0.45
        p_ft = o15 * 0.55
        st.write(f"Chance no 1º Tempo: **{p_ht:.1%}**")
        st.progress(min(100, int(p_ht * 100)))
        st.write(f"Chance no 2º Tempo: **{p_ft:.1%}**")
        st.progress(min(100, int(p_ft * 100)))

    with col_p2:
        st.subheader("📋 Base de Dados")
        hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
        hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
        hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
        st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.error("Erro ao carregar dados. Tente 'Forçar Atualização'.")
