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
    .player-row { background-color: #ffffff; padding: 10px; border-radius: 8px; border-bottom: 2px solid #e3f2fd; margin-bottom: 5px; font-size: 0.9em; }
    .label-time { font-weight: bold; color: #1e3a8a; margin-bottom: 10px; text-transform: uppercase; border-left: 5px solid #d1d5db; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS DE ELENCOS ATUALIZADOS (MARÇO/2026) ---
elencos = {
    "Tottenham": {
        "Defesa": ["Micky van de Ven", "Cristian Romero", "Radu Drăgușin", "Destiny Udogie"],
        "Meio": ["Archie Gray", "Lucas Bergvall", "James Maddison", "Pape Matar Sarr"],
        "Ataque": ["Dominic Solanke", "Brennan Johnson", "Wilson Odobert", "Dejan Kulusevski"]
    },
    "Crystal Palace": {
        "Defesa": ["Marc Guéhi", "Maxence Lacroix", "Daniel Muñoz", "Tyrick Mitchell"],
        "Meio": ["Adam Wharton", "Cheick Doucouré", "Daichi Kamada", "Jefferson Lerma"],
        "Ataque": ["Eberechi Eze", "Jean-Philippe Mateta", "Ismaïla Sarr", "Eddie Nketiah"]
    },
    "Arsenal": {
        "Defesa": ["William Saliba", "Gabriel Magalhães", "Jurriën Timber", "Riccardo Calafiori"],
        "Meio": ["Declan Rice", "Martin Ødegaard", "Mikel Merino", "Kai Havertz"],
        "Ataque": ["Bukayo Saka", "Gabriel Martinelli", "Leandro Trossard", "Raheem Sterling"]
    },
    "Man City": {
        "Defesa": ["Joško Gvardiol", "Rúben Dias", "Manuel Akanji", "Rico Lewis"],
        "Meio": ["Rodri", "Mateo Kovačić", "Phil Foden", "Ilkay Gündogan"],
        "Ataque": ["Erling Haaland", "Savinho", "Jeremy Doku", "Bernardo Silva"]
    },
    "Liverpool": {
        "Defesa": ["Virgil van Dijk", "Ibrahima Konaté", "Trent Alexander-Arnold", "Andy Robertson"],
        "Meio": ["Alexis Mac Allister", "Dominik Szoboszlai", "Ryan Gravenberch", "Harvey Elliott"],
        "Ataque": ["Mohamed Salah", "Luis Díaz", "Federico Chiesa", "Darwin Núñez"]
    },
    "Real Madrid": {
        "Defesa": ["Antonio Rüdiger", "Éder Militão", "Dani Carvajal", "Ferland Mendy"],
        "Meio": ["Jude Bellingham", "Federico Valverde", "Eduardo Camavinga", "Aurélien Tchouaméni"],
        "Ataque": ["Vinícius Júnior", "Kylian Mbappé", "Rodrygo", "Arda Güler"]
    },
    "Palmeiras": {
        "Defesa": ["Gustavo Gómez", "Murilo", "Agustín Giay", "Caio Paulista"],
        "Meio": ["Aníbal Moreno", "Richard Ríos", "Raphael Veiga", "Maurício"],
        "Ataque": ["Estêvão", "Flaco López", "Felipe Anderson", "Rony"]
    },
    "Flamengo": {
        "Defesa": ["Léo Pereira", "Fabrício Bruno", "Alex Sandro", "Wesley"],
        "Meio": ["Erick Pulgar", "Nicolás de la Cruz", "Gerson", "Carlos Alcaraz"],
        "Ataque": ["Pedro", "Gonzalo Plata", "Everton Cebolinha", "Michael"]
    }
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
st.title("🛡️ Terminal IA Elite: Scouts Atualizados 2026")

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

    # --- MÉTRICAS DE VALOR ---
    st.write("---")
    o15_p = 0
    for i in range(10):
        for j in range(10):
            if (i+j) > 1.5: o15_p += poisson.pmf(i, m_c_pro) * poisson.pmf(j, m_f_pro)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Prob. Over 1.5", f"{o15_p:.1%}")
    m2.metric("Proj. Cantos", f"{(m_c_pro*3.8 + m_f_pro*3.2):.1f}")
    m3.metric("Intensidade do Jogo", "ALTA" if (m_c_con + m_f_con) > 2.5 else "MÉDIA")

    # --- MONITORAMENTO PANORÂMICO 2026 ---
    st.write("---")
    st.subheader("🕵️ Scout por Jogador (Elenco Atualizado 2026)")
    setor = st.radio("Escolha o Setor:", ["Defesa", "Meio", "Ataque"], horizontal=True)
    
    col_a, col_b = st.columns(2)

    def render_players(time, setor_esc, g_sofridos, g_adv_pro):
        st.markdown(f"<div class='label-time'>{time}</div>", unsafe_allow_html=True)
        # Busca no banco 2026, se não achar usa placeholder
        jogadores = elencos.get(time, {}).get(setor_esc, [f"Jogador {setor_esc} 1", f"Jogador {setor_esc} 2"])
        
        for j in jogadores:
            # Faltas: Mais agressivo se o time sofre muitos gols
            # Desarmes: Mais agressivo se o adversário ataca muito
            f_est = (g_sofridos * 2.3) if setor_esc == "Defesa" else (g_sofridos * 1.6 if setor_esc == "Meio" else 0.7)
            d_est = (g_adv_pro * 2.6) if setor_esc == "Defesa" else (g_adv_pro * 1.9 if setor_esc == "Meio" else 0.5)
            
            st.markdown(f"""
                <div class='player-row'>
                    <b>{j}</b><br>
                    🔥 Est. Faltas: {f_est:.1f} | 🛡️ Est. Desarmes: {d_est:.1f}
                </div>
            """, unsafe_allow_html=True)

    with col_a: render_players(t_casa, setor, m_c_con, m_f_pro)
    with col_b: render_players(t_fora, setor, m_f_con, m_c_pro)

    # --- GESTÃO ---
    st.write("---")
    st.subheader("💰 Gestão de Banca")
    b1, b2 = st.columns(2)
    with b1: banca = st.number_input("Sua Banca (R$)", value=1000.0)
    with b2: 
        st.write("Sugestão de Entrada (Unidade 3%):")
        st.success(f"R$ {banca*0.03:.2f}")

    # --- HISTÓRICO ---
    st.subheader("📋 Histórico Recente")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    st.dataframe(hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True, hide_index=True)

else:
    st.error("Erro ao sincronizar dados da temporada 2026.")
