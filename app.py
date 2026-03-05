import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração de Layout
st.set_page_config(page_title="IA ELITE PREDICTOR 2026", layout="wide", page_icon="⚽")

# Estilo CSS Elite
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #d1d5db; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .lucro-texto { color: #28a745; font-weight: bold; font-size: 1.2em; }
    .player-row { background-color: #ffffff; padding: 10px; border-radius: 8px; border-bottom: 2px solid #e3f2fd; margin-bottom: 5px; font-size: 0.9em; }
    .label-time { font-weight: bold; color: #1e3a8a; margin-bottom: 10px; text-transform: uppercase; border-left: 5px solid #1e3a8a; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS DE ELENCOS (Adicionado Crystal Palace e outros) ---
elencos = {
    "Crystal Palace": {"Defesa": ["Marc Guéhi", "Maxence Lacroix", "Daniel Muñoz"], "Meio": ["Adam Wharton", "Cheick Doucouré", "Kamada"], "Ataque": ["Eberechi Eze", "Jean-Philippe Mateta", "Ismaïla Sarr"]},
    "Tottenham": {"Defesa": ["Romero", "Van de Ven", "Pedro Porro"], "Meio": ["Bissouma", "Pape Sarr", "James Maddison"], "Ataque": ["Heung-min Son", "Dominic Solanke", "Brennan Johnson"]},
    "Arsenal": {"Defesa": ["Saliba", "Gabriel Mag.", "Ben White"], "Meio": ["Declan Rice", "Odegaard", "Thomas Partey"], "Ataque": ["Bukayo Saka", "Kai Havertz", "Martinelli"]},
    "Man City": {"Defesa": ["Rúben Dias", "Akanji", "Gvardiol"], "Meio": ["Rodri", "De Bruyne", "Bernardo Silva"], "Ataque": ["Erling Haaland", "Phil Foden", "Jeremy Doku"]},
    "Real Madrid": {"Defesa": ["Rüdiger", "Militão", "Carvajal"], "Meio": ["Bellingham", "Valverde", "Tchouaméni"], "Ataque": ["Vinícius Jr", "Kylian Mbappé", "Rodrygo"]},
    "Liverpool": {"Defesa": ["Van Dijk", "Konaté", "Trent Alexander-Arnold"], "Meio": ["Mac Allister", "Szoboszlai", "Ryan Gravenberch"], "Ataque": ["Mohamed Salah", "Luis Díaz", "Darwin Núñez"]},
    "Chelsea": {"Defesa": ["Levi Colwill", "Wesley Fofana", "Reece James"], "Meio": ["Enzo Fernández", "Moisés Caicedo", "Cole Palmer"], "Ataque": ["Nicolas Jackson", "Nkunku", "Jadon Sancho"]},
    "Palmeiras": {"Defesa": ["Gustavo Gómez", "Murilo", "Marcos Rocha"], "Meio": ["Aníbal Moreno", "Richard Ríos", "Raphael Veiga"], "Ataque": ["Estêvão", "Flaco López", "Felipe Anderson"]},
    "Flamengo": {"Defesa": ["Léo Pereira", "Fabrício Bruno", "Ayrton Lucas"], "Meio": ["Erick Pulgar", "De la Cruz", "Gerson"], "Ataque": ["Pedro", "Everton Cebolinha", "Michael"]},
    "Barcelona": {"Defesa": ["Koundé", "Cubarsí", "Alejandro Balde"], "Meio": ["Pedri", "Frenkie de Jong", "Dani Olmo"], "Ataque": ["Lewandowski", "Lamine Yamal", "Raphinha"]}
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
    g_pro = g_con = 0
    for _, row in recent.iterrows():
        if row['HomeTeam'] == time:
            g_pro += row['FTHG']; g_con += row['FTAG']
        else:
            g_pro += row['FTAG']; g_con += row['FTHG']
    return (g_pro / 8), (g_con / 8), recent

# --- INTERFACE ---
st.title("🛡️ Terminal IA Elite: Scout Detalhado v17")

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

    m_c_pro, m_c_con, hist_casa = get_stats(df, t_casa)
    m_f_pro, m_f_con, hist_fora = get_stats(df, t_fora)

    # --- MÉTRICAS RÁPIDAS ---
    st.write("---")
    r1, r2, r3, r4 = st.columns(4)
    o15_prob = 0
    for i in range(10):
        for j in range(10):
            if (i+j) > 1.5: o15_prob += poisson.pmf(i, m_c_pro) * poisson.pmf(j, m_f_pro)
    
    r1.metric("Prob. Over 1.5", f"{o15_prob:.1%}")
    r2.metric("Média Gols/Jogo", f"{(m_c_pro + m_f_pro):.2f}")
    r3.metric("Proj. Cantos", f"{(m_c_pro*3.8 + m_f_pro*3.2):.1f}")
    r4.metric("Ambas Marcam", f"{(0.65 if (m_c_pro > 1 and m_f_pro > 1) else 0.45):.0%}")

    # --- VISÃO PANORÂMICA DE SCOUT ---
    st.write("---")
    st.subheader("👤 Monitoramento de Jogadores (Estimativa de Scout)")
    setor_alvo = st.radio("Selecione o Setor:", ["Defesa", "Meio", "Ataque"], horizontal=True)
    
    col_time_a, col_time_b = st.columns(2)

    def render_scout_list(time, setor, media_sofrida, media_adv_pro):
        st.markdown(f"<div class='label-time'>{time}</div>", unsafe_allow_html=True)
        # Se o time não estiver no dicionário, usa placeholder genérico
        jogadores = elencos.get(time, {}).get(setor, [f"Jogador {setor} 1", f"Jogador {setor} 2", f"Jogador {setor} 3"])
        
        for j in jogadores:
            # Cálculo de intensidade: Defesa foca em faltas por pressão, Meio em desarmes por combate
            f_est = (media_sofrida * 2.1) if setor == "Defesa" else (media_sofrida * 1.5 if setor == "Meio" else 0.8)
            d_est = (media_adv_pro * 1.8) if setor == "Meio" else (media_adv_pro * 2.4 if setor == "Defesa" else 0.4)
            
            st.markdown(f"""
                <div class='player-row'>
                    <b>{j}</b><br>
                    🔥 Est. Faltas: {f_est:.1f} | 🛡️ Est. Desarmes: {d_est:.1f}
                </div>
            """, unsafe_allow_html=True)

    with col_time_a:
        render_scout_list(t_casa, setor_alvo, m_c_con, m_f_pro)
    with col_time_b:
        render_scout_list(t_fora, setor_alvo, m_f_con, m_c_pro)

    # --- GESTÃO DE BANCA ---
    st.write("---")
    st.subheader("💰 Calculadora de Operação")
    b1, b2, b3 = st.columns(3)
    with b1: banca_op = st.number_input("Banca Total (R$)", value=1000.0)
    with b2: odd_op = st.number_input("Odd da Entrada", value=1.50)
    with b3:
        lucro_op = (banca_op * 0.03) * (odd_op - 1)
        st.write("Sugestão Stake Conservadora (3%):")
        st.success(f"R$ {banca_op*0.03:.2f} -> Retorno: R$ {lucro_op:.2f}")

    # --- HISTÓRICO ---
    st.write("---")
    st.subheader("📋 Histórico Recente (Data Limpa)")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
    hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
    st.dataframe(hist_view, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Aguardando sincronização... Clique em 'Forçar Atualização'.")
