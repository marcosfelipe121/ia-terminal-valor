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
    .stDataFrame { background-color: #ffffff; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        # Converte data e remove o horário 00:00:00
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

def get_stats(df, time):
    # Analisa os últimos 8 jogos para capturar a fase atual
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    gols_pro = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time: gols_pro += row['FTHG']
        else: gols_pro += row['FTAG']
    return (gols_pro / 8 if len(recent) > 0 else 0), recent

# --- TÍTULO E SIDEBAR ---
st.title("🛡️ Terminal IA Elite: Operacional & Lucro 2026")
st.caption("Sistema de Inteligência Estatística | Base de Dados Sincronizada")

if st.sidebar.button("♻️ Forçar Atualização de Dados"):
    st.cache_data.clear()
    st.rerun()

liga = st.sidebar.selectbox("🏆 Selecione a Liga", ["Premier League (ING)", "La Liga (ESP)", "Serie A (ITA)", "Série A (BRA)"])

# Mapeamento de URLs Oficiais (Temporada 25/26)
url_map = {
    "Premier League (ING)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "La Liga (ESP)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Serie A (ITA)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "Série A (BRA)": "https://www.football-data.co.uk/mmz4281/2526/BRA.csv"
}

df = load_data(url_map[liga])

if df is not None and not df.empty:
    # Seleção de Times
    times = sorted(df['HomeTeam'].unique())
    c1, c2 = st.columns(2)
    with c1: t_casa = st.selectbox("🏠 Mandante", times)
    with c2: t_fora = st.selectbox("🏃 Visitante", times, index=min(1, len(times)-1))

    # Cálculos de Médias
    m_casa, hist_casa = get_stats(df, t_casa)
    m_fora, hist_fora = get_stats(df, t_fora)

    # --- MOTOR DE PROBABILIDADES (POISSON) ---
    p_c = p_e = p_f = o15 = btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: p_c += prob
            elif i == j: p_e += prob
            else: p_f += prob
            if (i+j) > 1.5: o15 += prob
            if i > 0 and j > 0: btts += prob

    # --- DASHBOARD DE MÉTRICAS ---
    st.write("---")
    st.subheader("🎯 Probabilidades IA")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric(f"Vitória {t_casa}", f"{p_c:.1%}")
    d2.metric("Empate", f"{p_e:.1%}")
    d3.metric(f"Vitória {t_fora}", f"{p_f:.1%}")
    d4.metric("Ambas Marcam", f"{btts:.1%}")

    # --- GESTÃO DE APOSTA E LUCRO ---
    st.write("---")
    st.subheader("💰 Calculadora de Investimento e Lucro")
    
    col_stake, col_odd, col_lucro = st.columns([1, 1, 2])
    
    with col_stake:
        stake = st.number_input("Valor da Aposta (R$)", value=100.0, step=10.0)
    
    with col_odd:
        odd_atual = st.number_input("Odd Atual (Over 1.5)", value=1.25, step=0.01)
        
    with col_lucro:
        lucro_bruto = stake * odd_atual
        lucro_liquido = lucro_bruto - stake
        odd_justa = 1 / o15 if o15 > 0 else 0
        
        st.write(f"💵 **Retorno Total:** R$ {lucro_bruto:.2f}")
        st.markdown(f"💹 **Lucro Líquido:** <span class='lucro-texto'>R$ {lucro_liquido:.2f}</span>", unsafe_allow_html=True)
        
        if odd_atual > odd_justa:
            st.success(f"💎 VALOR ENCONTRADO! (Sugestão: Entrada de R$ {stake:.0f})")
        else:
            st.error(f"❌ SEM VALOR (Odd mínima aceitável: {odd_justa:.2f})")

    # --- MAPA DE CALOR E CANTOS ---
    st.write("---")
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("⛳ Escanteios & Tempo")
        # Projeção baseada em eficiência ofensiva
        proj_c = (m_casa * 3.5) + (m_fora * 3.0)
        st.metric("Projeção de Cantos", f"{proj_c:.1f}")
        
        # Tendências de tempo com porcentagem ao lado
        p_ht = o15 * 0.45
        p_ft = o15 * 0.55
        
        st.write(f"Chance de Gol no 1º Tempo: **{p_ht:.1%}**")
        st.progress(min(100, int(p_ht * 100)))
        
        st.write(f"Chance de Gol no 2º Tempo: **{p_ft:.1%}**")
        st.progress(min(100, int(p_ft * 100)))

    with col_p2:
        st.subheader("📋 Registro de Jogos (Dados Analisados)")
        # Combina e limpa histórico
        hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
        hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
        # Renomeando para Português
        hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
        st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ Erro ao conectar com a base de dados de 2026. Tente 'Forçar Atualização'.")
