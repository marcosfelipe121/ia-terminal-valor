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
    .player-row { background-color: #ffffff; padding: 10px; border-radius: 8px; border-bottom: 2px solid #e3f2fd; margin-bottom: 5px; font-size: 0.85em; }
    .label-time { font-weight: bold; color: #1e3a8a; margin-bottom: 10px; text-transform: uppercase; border-left: 5px solid #d1d5db; padding-left: 10px; }
    .warning-text { color: #856404; background-color: #fff3cd; padding: 5px; border-radius: 5px; font-size: 0.8em; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATABASE 2026: CHAMPIONS, PREMIER & LA LIGA ---
elencos = {
    # INGLATERRA
    "Man City": {"Defesa": ["Gvardiol", "Rúben Dias", "Akanji", "Rico Lewis"], "Meio": ["Rodri", "Kovačić", "Foden", "Gündogan"], "Ataque": ["Haaland", "Savinho", "Doku", "Bernardo Silva"]},
    "Arsenal": {"Defesa": ["Saliba", "Gabriel Mag.", "Timber", "Calafiori"], "Meio": ["Rice", "Ødegaard", "Merino", "Havertz"], "Ataque": ["Saka", "Martinelli", "Trossard", "Sterling"]},
    "Liverpool": {"Defesa": ["Van Dijk", "Konaté", "Alexander-Arnold", "Robertson"], "Meio": ["Mac Allister", "Szoboszlai", "Gravenberch", "Jones"], "Ataque": ["Salah", "Luis Díaz", "Nketiah", "Darwin Núñez"]},
    "Tottenham": {"Defesa": ["Van de Ven", "Romero", "Drăgușin", "Udogie"], "Meio": ["Archie Gray", "Bergvall", "Maddison", "Pape Sarr"], "Ataque": ["Solanke", "Brennan Johnson", "Odobert", "Kulusevski"]},
    "Chelsea": {"Defesa": ["Colwill", "Fofana", "Cucurella", "James"], "Meio": ["Enzo F.", "Caicedo", "Lavia", "Palmer"], "Ataque": ["Jackson", "Nkunku", "Sancho", "Madueke"]},
    "Man United": {"Defesa": ["De Ligt", "Lisandro Martínez", "Yoro", "Dalot"], "Meio": ["Mainoo", "Ugarte", "Bruno Fernandes", "Casemiro"], "Ataque": ["Højlund", "Rashford", "Garnacho", "Zirkzee"]},
    "Aston Villa": {"Defesa": ["Pau Torres", "Konsa", "Maatsen", "Diego Carlos"], "Meio": ["Onana", "Tielemans", "McGinn", "Ramsey"], "Ataque": ["Ollie Watkins", "Leon Bailey", "Rogers", "Durán"]},
    "Newcastle": {"Defesa": ["Botman", "Schär", "Hall", "Livramento"], "Meio": ["Bruno Guimarães", "Tonali", "Joelinton", "Willock"], "Ataque": ["Isak", "Gordon", "Barnes", "Almirón"]},
    "Crystal Palace": {"Defesa": ["Guéhi", "Lacroix", "Muñoz", "Mitchell"], "Meio": ["Wharton", "Doucouré", "Kamada", "Lerma"], "Ataque": ["Eze", "Mateta", "Ismaïla Sarr", "Nketiah"]},

    # ESPANHA
    "Real Madrid": {"Defesa": ["Rüdiger", "Militão", "Carvajal", "Mendy"], "Meio": ["Bellingham", "Valverde", "Camavinga", "Tchouaméni"], "Ataque": ["Vinícius Jr", "Mbappé", "Rodrygo", "Endrick"]},
    "Barcelona": {"Defesa": ["Koundé", "Cubarsí", "Araújo", "Balde"], "Meio": ["Pedri", "De Jong", "Gavi", "Dani Olmo"], "Ataque": ["Lewandowski", "Lamine Yamal", "Raphinha", "Ferran Torres"]},
    "Atlético Madrid": {"Defesa": ["Le Normand", "Giménez", "Reinildo", "Llorente"], "Meio": ["Gallagher", "De Paul", "Koke", "Barrios"], "Ataque": ["Julián Alvarez", "Griezmann", "Sorloth", "Correa"]},
    "Girona": {"Defesa": ["Blind", "David López", "Miguel G.", "Francés"], "Meio": ["Yangel Herrera", "Romeu", "Iván Martín", "Van de Beek"], "Ataque": ["Danjuma", "Miovski", "Tsygankov", "Asprilla"]},
    "Real Sociedad": {"Defesa": ["Aguerd", "Zubeldia", "Sergio Gómez", "Aramburu"], "Meio": ["Zubimendi", "Brais Méndez", "Sučić", "Turrientes"], "Ataque": ["Oyarzabal", "Becker", "Kubo", "Oskarsson"]},

    # CHAMPIONS (OUTROS GIGANTES)
    "Bayern Munich": {"Defesa": ["Kim Min-jae", "Upamecano", "Davies", "Boey"], "Meio": ["Kimmich", "Pavlović", "Musiala", "Palhinha"], "Ataque": ["Harry Kane", "Olise", "Sané", "Gnabry"]},
    "Leverkusen": {"Defesa": ["Tapsoba", "Tah", "Hincapié", "Frimpong"], "Meio": ["Xhaka", "Andrich", "Wirtz", "García"], "Ataque": ["Boniface", "Schick", "Adli", "Tella"]},
    "PSG": {"Defesa": ["Marquinhos", "Pacho", "Nuno Mendes", "Hakimi"], "Meio": ["Vitinha", "João Neves", "Zaïre-Emery", "Fabian Ruiz"], "Ataque": ["Barcola", "Dembélé", "Kolo Muani", "Gonçalo Ramos"]},
    "Inter": {"Defesa": ["Bastoni", "Pavard", "Acerbi", "Dimarco"], "Meio": ["Barella", "Calhanoglu", "Mkhitaryan", "Frattesi"], "Ataque": ["Lautaro Martínez", "Thuram", "Taremi", "Arnautovic"]},
    "Juventus": {"Defesa": ["Bremer", "Gatti", "Kalulu", "Cambiaso"], "Meio": ["Douglas Luiz", "Locatelli", "Koopmeiners", "Thuram"], "Ataque": ["Vlahovic", "Yildiz", "Nico González", "Conceição"]},
    "Borussia Dortmund": {"Defesa": ["Schlotterbeck", "Anton", "Couto", "Ryerson"], "Meio": ["Emre Can", "Gross", "Brandt", "Sabitzer"], "Ataque": ["Guirassy", "Adeyemi", "Beier", "Malen"]}
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
st.title("🛡️ Terminal IA Elite: Pro Predictor v21")

liga = st.sidebar.selectbox("🏆 Competição", ["Premier League (ING)", "La Liga (ESP)", "Serie A (ITA)", "Série A (BRA)"])
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

    # --- MÉTRICAS ---
    st.write("---")
    o15_p = 0
    for i in range(10):
        for j in range(10):
            if (i+j) > 1.5: o15_p += poisson.pmf(i, m_c_pro) * poisson.pmf(j, m_f_pro)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Prob. Over 1.5", f"{o15_p:.1%}")
    m2.metric("Proj. Cantos", f"{(m_c_pro*3.8 + m_f_pro*3.2):.1f}")
    m3.metric("Ambas Marcam", f"{(0.65 if m_c_pro > 1 and m_f_pro > 1 else 0.42):.0%}")
    m4.metric("Intensidade", "ALTA" if (m_c_con + m_f_con) > 2.3 else "MÉDIA")

    # --- MONITORAMENTO PANORÂMICO ---
    st.write("---")
    st.subheader("🕵️ Scout por Jogador (Database 2026)")
    setor = st.radio("Escolha o Setor:", ["Defesa", "Meio", "Ataque"], horizontal=True)
    
    col_pa, col_pb = st.columns(2)

    def render_players(time, setor_esc, g_sofridos, g_adv_pro):
        st.markdown(f"<div class='label-time'>{time}</div>", unsafe_allow_html=True)
        if time in elencos:
            jogadores = elencos[time].get(setor_esc, [])
        else:
            st.markdown("<div class='warning-text'>⚠️ Time fora da lista VIP.</div>", unsafe_allow_html=True)
            jogadores = [f"Jogador {setor_esc} 1", f"Jogador {setor_esc} 2"]
            
        for j in jogadores:
            f_est = (g_sofridos * 2.2) if setor_esc == "Defesa" else (g_sofridos * 1.5 if setor_esc == "Meio" else 0.6)
            d_est = (g_adv_pro * 2.5) if setor_esc == "Defesa" else (g_adv_pro * 1.8 if setor_esc == "Meio" else 0.4)
            st.markdown(f"<div class='player-row'><b>{j}</b><br>🔥 Faltas: {f_est:.1f} | 🛡️ Desarmes: {d_est:.1f}</div>", unsafe_allow_html=True)

    with col_pa: render_players(t_casa, setor, m_c_con, m_f_pro)
    with col_pb: render_players(t_fora, setor, m_f_con, m_c_pro)

    # --- GESTÃO DE BANCA ---
    st.write("---")
    st.subheader("💰 Gestão de Banca")
    gb1, gb2, gb3 = st.columns(3)
    with gb1: banca = st.number_input("Banca Total (R$)", value=1000.0)
    with gb2: odd_bt = st.number_input("Odd Bet365", value=1.25)
    with gb3:
        p_stake = 0.05 if o15_p > 0.8 else 0.02
        st.success(f"📈 Sugestão: R$ {banca * p_stake:.2f} ({(p_stake*100):.0f}%)")

    # --- HISTÓRICO ---
    st.write("---")
    st.subheader("📋 Últimos Resultados")
    hist_total = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    hist_view = hist_total[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].copy()
    hist_view.columns = ['Data', 'Mandante', 'Visitante', 'Gols Casa', 'Gols Fora']
    st.dataframe(hist_view, use_container_width=True, hide_index=True)

else: st.error("Erro ao carregar dados.")
