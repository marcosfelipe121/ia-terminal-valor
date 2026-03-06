import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Configuração da página
st.set_page_config(page_title="IA ELITE TERMINAL PRO", layout="wide", page_icon="⚽")

# -------------------------
# ESTILIZAÇÃO CSS
# -------------------------
st.markdown("""
<style>
.main {background:#f4f6fa;}
.stMetric {background:white;padding:12px;border-radius:10px;border:1px solid #ddd;}
.player-row {background:white;padding:8px;border-radius:6px;margin-bottom:5px;border-left:4px solid #2563eb; font-size: 13px;}
.label-time {font-weight:bold;font-size:18px;margin-bottom:8px; color: #1e40af; border-bottom: 2px solid #eee;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# DATABASE COMPLETA DE ELENCOS
# -------------------------
elencos = {
    # --- PREMIER LEAGUE (ING) ---
    "Man City": {"Defesa": ["Akanji", "Dias", "Gvardiol", "Walker"], "Meio": ["Rodri", "De Bruyne", "Foden", "Bernardo"], "Ataque": ["Haaland", "Doku", "Savinho", "Grealish"]},
    "Arsenal": {"Defesa": ["Saliba", "Gabriel", "White", "Timber"], "Meio": ["Rice", "Odegaard", "Havertz", "Merino"], "Ataque": ["Saka", "Martinelli", "Trossard", "Jesus"]},
    "Liverpool": {"Defesa": ["Van Dijk", "Konate", "Trent AA", "Robertson"], "Meio": ["Mac Allister", "Szoboszlai", "Gravenberch", "Jones"], "Ataque": ["Salah", "Diaz", "Nunez", "Jota"]},
    "Aston Villa": {"Defesa": ["Pau Torres", "Konsa", "Digne", "Cash"], "Meio": ["Tielemans", "Onana", "McGinn", "Ramsey"], "Ataque": ["Ollie Watkins", "Bailey", "Rogers", "Durán"]},
    "Tottenham": {"Defesa": ["Romero", "Van de Ven", "Porro", "Udogie"], "Meio": ["Maddison", "Bissouma", "Kulusevski", "Sarr"], "Ataque": ["Son", "Solanke", "Johnson", "Werner"]},
    "Chelsea": {"Defesa": ["Colwill", "Fofana", "Cucurella", "James"], "Meio": ["Enzo", "Caicedo", "Palmer", "Lavia"], "Ataque": ["Jackson", "Madueke", "Sancho", "Neto"]},
    "Newcastle": {"Defesa": ["Schär", "Burn", "Hall", "Livramento"], "Meio": ["Guimarães", "Tonali", "Joelinton", "Longstaff"], "Ataque": ["Isak", "Gordon", "Barnes", "Almirón"]},
    "Man United": {"Defesa": ["De Ligt", "Martinez", "Dalot", "Mazraoui"], "Meio": ["Mainoo", "Eriksen", "Fernandes", "Ugarte"], "Ataque": ["Rashford", "Hojlund", "Garnacho", "Zirkzee"]},
    "West Ham": {"Defesa": ["Kilman", "Todibo", "Emerson", "Wan-Bissaka"], "Meio": ["Soucek", "Rodriguez", "Paquetá", "Soler"], "Ataque": ["Bowen", "Kudus", "Antonio", "Fullkrug"]},
    "Brighton": {"Defesa": ["Dunk", "Van Hecke", "Estupiñán", "Veltman"], "Meio": ["Baleba", "Hinshelwood", "Mitoma", "Rutter"], "Ataque": ["Welbeck", "Pedro", "Minteh", "Ferguson"]},
    "Fulham": {"Defesa": ["Bassey", "Andersen", "Robinson", "Tete"], "Meio": ["Berge", "Pereira", "Smith Rowe", "Iwobi"], "Ataque": ["Jiménez", "Adama", "Nelson", "Muniz"]},
    "Brentford": {"Defesa": ["Pinnock", "Collins", "Ajer", "Van den Berg"], "Meio": ["Norgaard", "Janelt", "Damsgaard", "Jensen"], "Ataque": ["Mbeumo", "Wissa", "Schade", "Carvalho"]},
    "Bournemouth": {"Defesa": ["Senesi", "Zabarnyi", "Kerkez", "Smith"], "Meio": ["Cook", "Christie", "Kluivert", "Tavernier"], "Ataque": ["Evanilson", "Semenyo", "Sinisterra", "Ouattara"]},
    "Nott'm Forest": {"Defesa": ["Murillo", "Milenkovic", "Aina", "Moreno"], "Meio": ["Yates", "Ward-Prowse", "Gibbs-White", "Anderson"], "Ataque": ["Wood", "Elanga", "Hudson-Odoi", "Awoniyi"]},
    "Leicester": {"Defesa": ["Faes", "Okoli", "Kristiansen", "Justin"], "Meio": ["Winks", "Ndidi", "Buonanotte", "Skipp"], "Ataque": ["Vardy", "Mavididi", "Fatawu", "Ayew"]},
    "Everton": {"Defesa": ["Tarkowski", "Keane", "Mykolenko", "Young"], "Meio": ["Gueye", "Doucouré", "McNeil", "Mangala"], "Ataque": ["Calvert-Lewin", "Ndiaye", "Harrison", "Beto"]},
    "Ipswich": {"Defesa": ["O'Shea", "Greaves", "Davis", "Tuanzebe"], "Meio": ["Morsy", "Phillips", "Hutchinson", "Szmodics"], "Ataque": ["Delap", "Clarke", "Ogbene", "Hirst"]},
    "Crystal Palace": {"Defesa": ["Guehi", "Lacroix", "Munoz", "Mitchell"], "Meio": ["Lerma", "Wharton", "Kamada", "Eze"], "Ataque": ["Mateta", "Sarr", "Nketiah", "Schlupp"]},
    "Wolves": {"Defesa": ["Toti", "Dawson", "Ait-Nouri", "Semedo"], "Meio": ["Andre", "Lemina", "Gomes", "Bellegarde"], "Ataque": ["Cunha", "Larsen", "Hwang", "Guedes"]},
    "Southampton": {"Defesa": ["Bednarek", "Harwood-Bellis", "Walker-Peters", "Sugawara"], "Meio": ["Downes", "Aribo", "Fernandes", "Lallana"], "Ataque": ["Archer", "Brereton Díaz", "Armstrong", "Dibling"]},

    # --- LA LIGA (ESP) ---
    "Real Madrid": {"Defesa": ["Rüdiger", "Militão", "Carvajal", "Mendy"], "Meio": ["Bellingham", "Valverde", "Tchouaméni", "Camavinga"], "Ataque": ["Vinícius Jr", "Mbappé", "Rodrygo", "Endrick"]},
    "Barcelona": {"Defesa": ["Cubarsí", "Iñigo", "Koundé", "Balde"], "Meio": ["Pedri", "Casadó", "Olmo", "De Jong"], "Ataque": ["Lewandowski", "Yamal", "Raphinha", "Ferran"]},
    "Ath Madrid": {"Defesa": ["Le Normand", "Giménez", "Reinildo", "Molina"], "Meio": ["De Paul", "Gallagher", "Koke", "Llorente"], "Ataque": ["Griezmann", "Julián Álvarez", "Sørloth", "Correa"]},
    "Botafogo": {"Defesa": ["Bastos", "Barboza", "Vitinho", "Cuiabano"], "Meio": ["Gregore", "Marlon Freitas", "Almada", "Savarin"], "Ataque": ["Luiz Henrique", "Igor Jesus", "Tiquinho", "Júnior Santos"]},
    "Palmeiras": {"Defesa": ["Gustavo Gómez", "Murilo", "Marcos Rocha", "Caio Paulista"], "Meio": ["Aníbal Moreno", "Richard Ríos", "Veiga", "Maurício"], "Ataque": ["Estêvão", "Flaco López", "Felipe Anderson", "Rony"]},
    "Flamengo": {"Defesa": ["Léo Pereira", "Fabrício Bruno", "Wesley", "Alex Sandro"], "Meio": ["Pulgar", "De La Cruz", "Arrascaeta", "Gerson"], "Ataque": ["Bruno Henrique", "Gabriel Barbosa", "Michael", "Plata"]},
}

# -------------------------
# FUNÇÕES DE CÁLCULO
# -------------------------
@st.cache_data(ttl=7200)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines="skip")
        # Padronização de datas para evitar erros de formato
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors="coerce").dt.date
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def team_stats(df, team):
    jogos = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(12)
    if len(jogos) == 0: 
        return 0, 0, "N/A", jogos
    
    g_pro = 0
    g_con = 0
    forma = []
    for _, row in jogos.iterrows():
        if row['HomeTeam'] == team:
            g_pro += row['FTHG']; g_con += row['FTAG']
            res = "🟢" if row['FTHG'] > row['FTAG'] else "🟡" if row['FTHG'] == row['FTAG'] else "🔴"
        else:
            g_pro += row['FTAG']; g_con += row['FTHG']
            res = "🟢" if row['FTAG'] > row['FTHG'] else "🟡" if row['FTAG'] == row['FTHG'] else "🔴"
        forma.append(res)
    
    media_pro = g_pro / len(jogos)
    media_con = g_con / len(jogos)
    return media_pro, media_con, "".join(forma[-5:]), jogos

def poisson_model(exp_home, exp_away):
    p_home = p_draw = p_away = btts = o15 = o25 = o35 = 0
    scores = {}
    for i in range(7):
        for j in range(7):
            prob = poisson.pmf(i, exp_home) * poisson.pmf(j, exp_away)
            if i > j: p_home += prob
            elif i == j: p_draw += prob
            else: p_away += prob
            if i > 0 and j > 0: btts += prob
            if (i+j) > 1.5: o15 += prob
            if (i+j) > 2.5: o25 += prob
            if (i+j) > 3.5: o35 += prob
            scores[f"{i}-{j}"] = prob
            
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    return p_home, p_draw, p_away, btts, o15, o25, o35, sorted_scores

def kelly(prob, odd, banca, frac=0.4):
    if odd <= 1: return 0
    k = ((odd * prob) - 1) / (odd - 1)
    return max(0, banca * k * frac)

# -------------------------
# INTERFACE
# -------------------------
st.title("⚽ IA ELITE TERMINAL PRO v2.0")

liga = st.sidebar.selectbox("Liga", ["Premier League", "La Liga", "Brasileirão"])
url_map = {
    "Premier League": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "La Liga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "Brasileirão": "https://www.football-data.co.uk/mmz4281/2425/BRA.csv"
}

df_data = load_data(url_map[liga])

if not df_data.empty:
    times = sorted(df_data['HomeTeam'].unique())

    col1, col2 = st.columns(2)
    with col1: t_casa = st.selectbox("Mandante", times, index=0)
    with col2: t_fora = st.selectbox("Visitante", times, index=min(1, len(times)-1))

    # Processamento
    m_c_pro, m_c_con, forma_c, hist_casa = team_stats(df_data, t_casa)
    m_f_pro, m_f_con, forma_f, hist_fora = team_stats(df_data, t_fora)
    
    exp_casa = (m_c_pro + m_f_con) / 2
    exp_fora = (m_f_pro + m_c_con) / 2
    
    p_c, p_e, p_f, btts, o15, o25, o35, placares = poisson_model(exp_casa, exp_fora)

    # Exibição de Métricas
    st.subheader("📊 Probabilidades")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{t_casa}", f"{p_c:.1%}", f"Forma: {forma_c}", delta_color="off")
    m2.metric("Empate", f"{p_e:.1%}")
    m3.metric(f"{t_fora}", f"{p_f:.1%}", f"Forma: {forma_f}", delta_color="off")
    m4.metric("AM (BTTS)", f"{btts:.1%}")

    # Scout de Jogadores
    st.subheader("🕵️ Scout de Jogadores (Projeção)")
    setor = st.radio("Selecione o Setor", ["Defesa", "Meio", "Ataque"], horizontal=True)

    def render_scout(team, setor, m_sofridos, m_pro):
        st.markdown(f"<div class='label-time'>{team}</div>", unsafe_allow_html=True)
        jogadores = elencos.get(team, {}).get(setor, ["Titular A", "Titular B", "Reserva A", "Reserva B"])
        
        for j in jogadores:
            desarmes = (m_sofridos * 2.1) + np.random.uniform(0.1, 1.2)
            chutes = (m_pro * 1.3) + np.random.uniform(0.1, 1.0)
            passes = 85 + np.random.uniform(-5, 10)
            
            st.markdown(f"""
            <div class='player-row'>
            <b>{j}</b> | 🛡️ Desarmes: {desarmes:.1f} | 🎯 Chutes: {chutes:.1f} | 📈 Passes: {passes:.0f}%
            </div>
            """, unsafe_allow_html=True)

    cs1, cs2 = st.columns(2)
    with cs1: render_scout(t_casa, setor, m_c_con, m_c_pro)
    with cs2: render_scout(t_fora, setor, m_f_con, m_f_pro)

    # Value Bets
    st.divider()
    st.subheader("💰 Inserir Odds para Scanner")
    o1, o2, o3 = st.columns(3)
    with o1: odd_casa = st.number_input(f"Odd {t_casa}", value=2.0, step=0.01)
    with o2: banca = st.number_input("Banca Total (R$)", value=1000.0, step=50.0)
    with o3: 
        stake = kelly(p_c, odd_casa, banca)
        st.write(f"**Sugestão de Stake:** R$ {stake:.2f}")

    if (p_c * odd_casa) > 1.05:
        st.success(f"🔥 VALOR ENCONTRADO! Invista R$ {stake:.2f} no {t_casa}")
    else:
        st.warning("⚠️ Sem valor matemático claro nesta odd.")

    st.subheader("🎯 Placares Mais Prováveis")
    df_placares = pd.DataFrame(placares, columns=["Placar", "Probabilidade"])
    df_placares["Probabilidade"] = df_placares["Probabilidade"].map("{:.2%}".format)
    st.table(df_placares)

    st.subheader("📋 Histórico Recente")
    hist_view = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values(by='Date', ascending=False)
    st.dataframe(hist_view[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']], use_container_width=True)
else:
    st.error("Não foi possível carregar os dados da liga selecionada.")
