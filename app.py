import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout Profissional
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Estilo CSS Restaurado e Aprimorado
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .lucro-texto { color: #28a745; font-weight: bold; font-size: 1.2em; }
    .scout-card { background-color: #e3f2fd; padding: 15px; border-radius: 10px; border-left: 5px solid #2196f3; margin-bottom: 10px; }
    .player-card { background-color: #fff3e0; padding: 15px; border-radius: 10px; border: 1px solid #ffb74d; }
    </style>
    """, unsafe_allow_html=True)

# Banco de Dados de Jogadores (Exemplos Principais 2026)
elencos = {
    "Tottenham": {"Defesa": ["Romero", "Van de Ven"], "Meio": ["Bissouma", "Sarr", "Maddison"], "Ataque": ["Son", "Solanke"]},
    "Arsenal": {"Defesa": ["Saliba", "Gabriel Mag."], "Meio": ["Rice", "Odegaard"], "Ataque": ["Saka", "Havertz"]},
    "Real Madrid": {"Defesa": ["Rüdiger", "Militão"], "Meio": ["Bellingham", "Valverde", "Tchouaméni"], "Ataque": ["Vinícius Jr", "Mbappé"]},
    "Man City": {"Defesa": ["Dias", "Akanji"], "Meio": ["Rodri", "De Bruyne"], "Ataque": ["Haaland", "Foden"]},
    "Palmeiras": {"Defesa": ["Gustavo Gómez", "Murilo"], "Meio": ["Aníbal Moreno", "Richard Ríos"], "Ataque": ["Estêvão", "Flaco López"]},
    "Flamengo": {"Defesa": ["Léo Pereira", "Fabrício Bruno"], "Meio": ["Pulgar", "De la Cruz"], "Ataque": ["Pedro", "Cebolinha"]}
}

@st.cache_data(ttl=3600)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
        return df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
    except: return None

def get_stats(df, time):
    recent = df[(df['HomeTeam'] == time) | (df['AwayTeam'] == time)].tail(8)
    g_pro = 0; g_con = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time:
            g_pro += row['FTHG']; g_con += row['FTAG']
        else:
            g_pro += row['FTAG']; g_con += row['FTHG']
    return (g_pro / 8), (g_con / 8), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite Predictor Pro v15")

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

    m_c_pro, m_c_con, hist_casa = get_stats(df, t_casa)
    m_f_pro, m_f_con, hist_fora = get_stats(df, t_fora)

    # --- PROBABILIDADES ---
    p_c = p_e = p_f = o15 = btts = 0
    for i in range(12):
        for j in range(12):
            prob = poisson.pmf(i, m_c_pro) * poisson.pmf(j, m_f_pro)
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

    # --- GESTÃO DE BANCA E LUCRO (RESTAURADO) ---
    st.write("---")
    st.subheader("💰 Gestão de Banca & Valor")
    col_b, col_o, col_r = st.columns([1, 1, 2])
    with col_b: banca = st.number_input("Banca Total (R$)", value=1000.0)
    with col_o: odd_casa = st.number_input("Odd Bet365 (Over 1.5)", value=1.25)
    with col_r:
        odd_j = 1/o15 if o15 > 0 else 0
        ev = (o15 * odd_casa) - 1
        lucro_l = (banca * 0.05) * (odd_casa - 1)
        if ev > 0.05:
            st.success(f"💎 VALOR! Sugestão: R$ {banca*0.05:.2f} (5%) | Lucro Líquido: R$ {lucro_l:.2f}")
        else:
            st.error(f"❌ SEM VALOR! Sugestão: R$ {banca*0.01:.2f} (1%) | Odd Mínima: {odd_j:.2f}")

    # --- SCOUT DETALHADO POR SETOR ---
    st.write("---")
    st.subheader("🕵️ Análise de Intensidade & Scout")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"<div class='scout-card'><b>{t_casa} (Defensivo)</b><br>Faltas Cometidas Est.: {m_c_con * 8.8:.1f} (Base Gols Sofridos)<br>Desarmes Est.: {m_f_pro * 11.5:.1f} (Base Ataque Adv)</div>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"<div class='scout-card'><b>{t_fora} (Defensivo)</b><br>Faltas Cometidas Est.: {m_f_con * 9.2:.1f}<br>Desarmes Est.: {m_c_pro * 11.2:.1f}</div>", unsafe_allow_html=True)

    # --- PLAYER PROPS COM JOGADORES REAIS ---
    st.write("---")
    st.subheader("👤 Player Props: Estimativa por Jogador")
    p1, p2, p3 = st.columns(3)
    
    with p1:
        setor = st.selectbox("Setor do Jogador", ["Defesa", "Meio", "Ataque"])
    with p2:
        # Puxa jogadores do elenco se existirem, senão coloca genérico
        lista_jogadores = elencos.get(t_casa, {}).get(setor, ["Jogador 1", "Jogador 2"])
        nome_j = st.selectbox("Selecione o Jogador", lista_jogadores)
    with p3:
        agressividade = st.select_slider("Perfil de Jogo", options=["Cidadozo", "Normal", "Agressivo"], value="Normal")

    # Lógica de cálculo do jogador
    mult_ag = 0.8 if agressividade == "Cidadozo" else (1.3 if agressividade == "Normal" else 2.1)
    est_faltas = (m_c_con * 0.9) * mult_ag
    est_desarmes = (m_f_pro * 1.2) * mult_ag

    st.markdown(f"""
    <div class='player-card'>
    ⚽ Jogador: <b>{nome_j}</b> ({t_casa}) | Setor: {setor}<br>
    🔥 Estimativa de Faltas: <b>{est_faltas:.2f}</b> | 🛡️ Estimativa de Desarmes: <b>{est_desarmes:.2f}</b>
    </div>
    """, unsafe_allow_html=True)

    # --- REGISTRO E MAPA ---
    st.write("---")
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        st.subheader("⛳ Escanteios & Tempo")
        proj_c = (m_c_pro * 3.5) + (m_f_pro * 3.0)
        st.metric("Projeção de Cantos", f"{proj_c:.1f}")
        st.write(f"Chance Gol 1T: **{o15*0.45:.1%}**")
        st.progress(min(100, int(o15*45)))
        st.write(f"Chance Gol 2T: **{o15*0.55:.1%}**")
        st.progress(min(100, int(o15*55)))
    with col_p2:
        st.subheader("📋 Registro de Dados")
        hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
        hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
        hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
        st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.error("Erro na base. Clique em 'Forçar Atualização'.")
