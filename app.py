import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="IA ELITE PRO v3", 
    layout="wide", 
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card2: #1a2235;
    --accent-green: #00f5a0;
    --accent-blue: #3b82f6;
    --accent-orange: #f97316;
    --accent-red: #ef4444;
    --accent-yellow: #fbbf24;
    --text-primary: #f0f4ff;
    --text-secondary: #94a3b8;
    --border: #1e293b;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; letter-spacing: 0.05em; }

.main-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00f5a0, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: 0.08em;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #4ade80;
    text-align: center;
    letter-spacing: 0.3em;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00f5a0, #3b82f6);
}

.metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-secondary);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--accent-green);
    line-height: 1;
}

.metric-sub {
    font-size: 0.7rem;
    color: var(--text-secondary);
    margin-top: 4px;
    font-family: 'Inter', sans-serif;
}

.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.08em;
    padding: 12px 0 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.player-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: border-color 0.2s;
}

.player-card:hover { border-color: var(--accent-blue); }

.player-name {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-primary);
}

.player-stats {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-secondary);
    display: flex;
    gap: 12px;
}

.stat-pill {
    background: #1e293b;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
}

.value-bet-card {
    background: linear-gradient(135deg, #052e16, #14532d);
    border: 1px solid #16a34a;
    border-radius: 12px;
    padding: 16px 20px;
}

.no-value-card {
    background: #1c1106;
    border: 1px solid #92400e;
    border-radius: 12px;
    padding: 16px 20px;
}

.odds-scanner-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.team-badge {
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 16px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--text-primary);
    text-align: center;
    margin-bottom: 12px;
}

.forma-circle {
    display: inline-block;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    font-size: 10px;
    line-height: 18px;
    text-align: center;
    margin: 1px;
}

.stSelectbox > div > div, .stNumberInput > div > div > input, .stRadio > div {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

div[data-testid="stMetric"] label { color: var(--text-secondary) !important; font-size: 0.75rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--accent-green) !important; font-family: 'Rajdhani', sans-serif !important; font-size: 1.8rem !important; }

.stDataFrame { background: var(--bg-card) !important; }
table { background: var(--bg-card) !important; color: var(--text-primary) !important; }

.divider-line {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
}

.confidence-bar-bg {
    background: #1e293b;
    border-radius: 4px;
    height: 6px;
    margin-top: 6px;
    overflow: hidden;
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #00f5a0, #3b82f6);
}

.tip-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.08em;
}

.tip-value { background: #052e16; color: #4ade80; border: 1px solid #16a34a; }
.tip-warning { background: #1c1106; color: #fb923c; border: 1px solid #c2410c; }
.tip-info { background: #172554; color: #93c5fd; border: 1px solid #1d4ed8; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# DATABASE COMPLETA DE ELENCOS
# -------------------------
elencos = {
    # PREMIER LEAGUE
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
    # LA LIGA
    "Real Madrid": {"Defesa": ["Rüdiger", "Militão", "Carvajal", "Mendy"], "Meio": ["Bellingham", "Valverde", "Tchouaméni", "Camavinga"], "Ataque": ["Vinícius Jr", "Mbappé", "Rodrygo", "Endrick"]},
    "Barcelona": {"Defesa": ["Cubarsí", "Iñigo", "Koundé", "Balde"], "Meio": ["Pedri", "Casadó", "Olmo", "De Jong"], "Ataque": ["Lewandowski", "Yamal", "Raphinha", "Ferran"]},
    "Ath Madrid": {"Defesa": ["Le Normand", "Giménez", "Reinildo", "Molina"], "Meio": ["De Paul", "Gallagher", "Koke", "Llorente"], "Ataque": ["Griezmann", "Julián Álvarez", "Sørloth", "Correa"]},
    "Girona": {"Defesa": ["Blind", "David López", "Miguel", "Francés"], "Meio": ["Herrera", "Martin", "Van de Beek", "Romeu"], "Ataque": ["Miovski", "Tsygankov", "Danjuma", "Bryan Gil"]},
    "Ath Bilbao": {"Defesa": ["Vivian", "Yeray", "Yuri", "De Marcos"], "Meio": ["Prados", "Galarreta", "Sancet", "Unai Gómez"], "Ataque": ["Iñaki Williams", "Nico Williams", "Guruzeta", "Berenguer"]},
    "Real Sociedad": {"Defesa": ["Zubeldia", "Aguerd", "Javi López", "Aramburu"], "Meio": ["Zubimendi", "Sučić", "Brais Méndez", "Turrientes"], "Ataque": ["Oyarzabal", "Becker", "Kubo", "Óskarsson"]},
    "Villarreal": {"Defesa": ["Albiol", "Costa", "Cardona", "Femenía"], "Meio": ["Parejo", "Comesaña", "Baena", "Pino"], "Ataque": ["Ayoze Pérez", "Barry", "Gerard Moreno", "Pépé"]},
    "Betis": {"Defesa": ["Natan", "Llorente", "Perraud", "Bellerín"], "Meio": ["Roca", "Johnny", "Lo Celso", "Fornals"], "Ataque": ["Vitor Roque", "Abde", "Chimy Ávila", "Bakambu"]},
    "Sevilla": {"Defesa": ["Badé", "Marcao", "Barco", "Carmona"], "Meio": ["Gudelj", "Agoumé", "Lokonga", "Saúl"], "Ataque": ["Isaac Romero", "Lukebakio", "Ejuke", "Iheanacho"]},
    "Valencia": {"Defesa": ["Mosquera", "Tárrega", "Gayà", "Correia"], "Meio": ["Pepelu", "Guillamón", "Guerra", "Almeida"], "Ataque": ["Hugo Duro", "Diego López", "Rioja", "Dani Gómez"]},
    # BRASILEIRÃO
    "Botafogo": {"Defesa": ["Bastos", "Barboza", "Vitinho", "Cuiabano"], "Meio": ["Gregore", "Marlon Freitas", "Almada", "Savarin"], "Ataque": ["Luiz Henrique", "Igor Jesus", "Tiquinho", "Júnior Santos"]},
    "Palmeiras": {"Defesa": ["Gustavo Gómez", "Murilo", "Marcos Rocha", "Caio Paulista"], "Meio": ["Aníbal Moreno", "Richard Ríos", "Veiga", "Maurício"], "Ataque": ["Estêvão", "Flaco López", "Felipe Anderson", "Rony"]},
    "Flamengo": {"Defesa": ["Léo Pereira", "Fabrício Bruno", "Wesley", "Alex Sandro"], "Meio": ["Pulgar", "De La Cruz", "Arrascaeta", "Gerson"], "Ataque": ["Bruno Henrique", "Gabriel Barbosa", "Michael", "Plata"]},
    "Fortaleza": {"Defesa": ["Kuscevic", "Cardona", "Tinga", "Bruno Pacheco"], "Meio": ["Hércules", "Zé Welison", "Pochettino", "Lucas Sasha"], "Ataque": ["Lucero", "Pikachu", "Moisés", "Marinho"]},
    "Internacional": {"Defesa": ["Vitão", "Rogel", "Bernabei", "Bruno Gomes"], "Meio": ["Fernando", "Thiago Maia", "Alan Patrick", "Gabriel Carvalho"], "Ataque": ["Borré", "Enner Valencia", "Wanderson", "Wesley"]},
    "São Paulo": {"Defesa": ["Arboleda", "Alan Franco", "Rafinha", "Welington"], "Meio": ["Luiz Gustavo", "Bobadilla", "Lucas", "Luciano"], "Ataque": ["Calleri", "Ferreira", "Erick", "André Silva"]},
    "Cruzeiro": {"Defesa": ["João Marcelo", "Villalba", "William", "Marlon"], "Meio": ["Walace", "Matheus Henrique", "Matheus Pereira", "Barreal"], "Ataque": ["Kaio Jorge", "Gabriel Veron", "Lautaro", "Dinenno"]},
    "Bahia": {"Defesa": ["Kanu", "Gabriel Xavier", "Arias", "Luciano Juba"], "Meio": ["Caio Alexandre", "Jean Lucas", "Everton Ribeiro", "Cauly"], "Ataque": ["Thaciano", "Everaldo", "Lucho", "Ademir"]},
    "Vasco": {"Defesa": ["João Victor", "Maicon", "Lucas Piton", "Paulo Henrique"], "Meio": ["Hugo Moura", "Mateus Carvalho", "Payet", "Coutinho"], "Ataque": ["Vegetti", "Emerson Rodríguez", "David", "Rayan"]},
    "Atlético-MG": {"Defesa": ["Battaglia", "Junior Alonso", "Arana", "Saravia"], "Meio": ["Otávio", "Alan Franco", "Scarpa", "Zaracho"], "Ataque": ["Hulk", "Paulinho", "Deyverson", "Vargas"]},
    "Grêmio": {"Defesa": ["Jemerson", "Ely", "Reinaldo", "João Pedro"], "Meio": ["Villasanti", "Dodi", "Cristaldo", "Edenilson"], "Ataque": ["Braithwaite", "Soteldo", "Pavon", "Diego Costa"]},
    "Corinthians": {"Defesa": ["André Ramalho", "Gustavo Henrique", "Matheuzinho", "Hugo"], "Meio": ["José Martínez", "Breno Bidon", "Garro", "Carrillo"], "Ataque": ["Memphis Depay", "Yuri Alberto", "Romero", "Hernández"]},
    "Fluminense": {"Defesa": ["Thiago Silva", "Thiago Santos", "Samuel Xavier", "Marcelo"], "Meio": ["Facundo Bernal", "Martinelli", "Ganso", "Arias"], "Ataque": ["Kauã Elias", "Keno", "Serna", "Cano"]},
    "Athletico-PR": {"Defesa": ["Kaique Rocha", "Thiago Heleno", "Esquivel", "Madson"], "Meio": ["Erick", "Fernandinho", "Zapelli", "Christian"], "Ataque": ["Mastriani", "Canobbio", "Cuello", "Pablo"]},
}

# -------------------------
# FUNÇÕES DE CÁLCULO
# -------------------------
@st.cache_data(ttl=7200)
def load_data(url):
    try:
        df = pd.read_csv(url, on_bad_lines="skip")
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors="coerce").dt.date
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def team_stats(df, team, n=12):
    jogos = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].tail(n)
    if len(jogos) == 0: return 0, 0, [], jogos, 0, 0
    g_pro, g_con, vitorias, empates, derrotas = 0, 0, 0, 0, 0
    forma = []
    for _, row in jogos.iterrows():
        if row['HomeTeam'] == team:
            g_pro += row['FTHG']; g_con += row['FTAG']
            if row['FTHG'] > row['FTAG']: forma.append('W'); vitorias += 1
            elif row['FTHG'] == row['FTAG']: forma.append('D'); empates += 1
            else: forma.append('L'); derrotas += 1
        else:
            g_pro += row['FTAG']; g_con += row['FTHG']
            if row['FTAG'] > row['FTHG']: forma.append('W'); vitorias += 1
            elif row['FTAG'] == row['FTHG']: forma.append('D'); empates += 1
            else: forma.append('L'); derrotas += 1
    pts = vitorias * 3 + empates
    pts_max = len(jogos) * 3
    return g_pro/len(jogos), g_con/len(jogos), forma[-5:], jogos, pts/pts_max if pts_max else 0, len(jogos)

def poisson_model(exp_home, exp_away):
    p_home=p_draw=p_away=btts=o15=o25=o35=0
    scores={}
    for i in range(8):
        for j in range(8):
            prob = poisson.pmf(i, exp_home) * poisson.pmf(j, exp_away)
            if i > j: p_home += prob
            elif i == j: p_draw += prob
            else: p_away += prob
            if i > 0 and j > 0: btts += prob
            if (i+j) > 1.5: o15 += prob
            if (i+j) > 2.5: o25 += prob
            if (i+j) > 3.5: o35 += prob
            scores[f"{i}-{j}"] = prob
    top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:6]
    return p_home, p_draw, p_away, btts, o15, o25, o35, top5

def kelly_criterion(prob, odd, banca, frac=0.3):
    edge = (odd * prob) - 1
    k = edge / (odd - 1) if odd > 1 else 0
    return max(0, banca * k * frac), edge

def expected_value(prob, odd):
    return (prob * (odd - 1)) - (1 - prob)

def home_away_split(jogos, team):
    home = jogos[jogos['HomeTeam'] == team]
    away = jogos[jogos['AwayTeam'] == team]
    home_gp = home['FTHG'].mean() if len(home) > 0 else 0
    home_gc = home['FTAG'].mean() if len(home) > 0 else 0
    away_gp = away['FTAG'].mean() if len(away) > 0 else 0
    away_gc = away['FTHG'].mean() if len(away) > 0 else 0
    return home_gp, home_gc, away_gp, away_gc

# -------------------------
# INTERFACE
# -------------------------

# Header
st.markdown('<div class="main-title">⚽ IA ELITE TERMINAL PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">[ SISTEMA DE ANÁLISE PREDITIVA v3.0 — MODELO POISSON + KELLY ]</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    liga = st.selectbox("🌍 Liga", ["Premier League", "La Liga", "Brasileirão"])
    st.markdown("---")
    banca = st.number_input("💰 Banca Total (R$)", min_value=100.0, value=1000.0, step=50.0)
    frac_kelly = st.slider("Fração Kelly", 0.1, 1.0, 0.3, 0.05)
    st.markdown("---")
    st.markdown("### 📊 Sobre o Modelo")
    st.caption("Modelo Poisson + Critério de Kelly para gestão de banca. Dados históricos via football-data.co.uk")
    st.caption("⚠️ Use com responsabilidade. Aposte apenas o que pode perder.")

url_map = {
    "Premier League": "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "La Liga": "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "Brasileirão": "https://www.football-data.co.uk/mmz4281/2425/BRA.csv"
}

with st.spinner("🔄 Carregando dados..."):
    df = load_data(url_map[liga])

if df.empty:
    st.error("Não foi possível carregar os dados. Verifique a conexão.")
    st.stop()

times = sorted(set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique()))

col1, col2 = st.columns(2)
with col1:
    t_casa = st.selectbox("🏠 Mandante", times, index=0)
with col2:
    t_fora = st.selectbox("✈️ Visitante", times, index=min(1, len(times)-1))

if t_casa == t_fora:
    st.warning("⚠️ Selecione times diferentes.")
    st.stop()

# Estatísticas
m_c_pro, m_c_con, forma_c, hist_casa, perc_c, n_c = team_stats(df, t_casa)
m_f_pro, m_f_con, forma_f, hist_fora, perc_f, n_f = team_stats(df, t_fora)

# Vantagem de mando
exp_casa = (m_c_pro * 1.1 + m_f_con) / 2
exp_fora = (m_f_pro * 0.9 + m_c_con) / 2

p_c, p_e, p_f, btts, o15, o25, o35, placares = poisson_model(exp_casa, exp_fora)
hc_gp, hc_gc, hc_agp, hc_agc = home_away_split(hist_casa, t_casa)
hf_gp, hf_gc, hf_agp, hf_agc = home_away_split(hist_fora, t_fora)

# -------------------------
# SEÇÃO 1: HEADER DO CONFRONTO
# -------------------------
st.markdown("<hr class='divider-line'>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 1, 2])
with c1:
    st.markdown(f"<div class='team-badge'>🏠 {t_casa}</div>", unsafe_allow_html=True)
    forma_html = ""
    for r in forma_c:
        cor = "#4ade80" if r == 'W' else "#fbbf24" if r == 'D' else "#f87171"
        letra = r
        forma_html += f"<span style='background:{cor};color:#111;display:inline-block;width:22px;height:22px;border-radius:50%;text-align:center;line-height:22px;font-size:11px;font-weight:700;margin:1px;font-family:monospace'>{letra}</span>"
    st.markdown(f"<div style='text-align:center'>Forma: {forma_html}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;margin-top:8px;font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#94a3b8'>⚽ {m_c_pro:.2f} gols/jogo | 🛡️ {m_c_con:.2f} sofridos</div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<div style='text-align:center;font-family:Rajdhani,sans-serif;font-size:2rem;font-weight:700;color:#64748b;padding:20px 0'>VS</div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='team-badge'>✈️ {t_fora}</div>", unsafe_allow_html=True)
    forma_html2 = ""
    for r in forma_f:
        cor = "#4ade80" if r == 'W' else "#fbbf24" if r == 'D' else "#f87171"
        forma_html2 += f"<span style='background:{cor};color:#111;display:inline-block;width:22px;height:22px;border-radius:50%;text-align:center;line-height:22px;font-size:11px;font-weight:700;margin:1px;font-family:monospace'>{r}</span>"
    st.markdown(f"<div style='text-align:center'>Forma: {forma_html2}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;margin-top:8px;font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#94a3b8'>⚽ {m_f_pro:.2f} gols/jogo | 🛡️ {m_f_con:.2f} sofridos</div>", unsafe_allow_html=True)

# -------------------------
# SEÇÃO 2: PROBABILIDADES
# -------------------------
st.markdown("---")
st.markdown('<div class="section-header">📊 PROBABILIDADES DO MODELO</div>', unsafe_allow_html=True)

m1, m2, m3, m4, m5 = st.columns(5)
cards = [
    (f"🏠 {t_casa[:10]}", f"{p_c:.1%}", f"Odd justa: {1/p_c:.2f}"),
    ("🤝 Empate", f"{p_e:.1%}", f"Odd justa: {1/p_e:.2f}"),
    (f"✈️ {t_fora[:10]}", f"{p_f:.1%}", f"Odd justa: {1/p_f:.2f}"),
    ("🔀 Ambos Marcam", f"{btts:.1%}", f"Odd justa: {1/btts:.2f}"),
    ("🎯 +2.5 Gols", f"{o25:.1%}", f"Odd justa: {1/o25:.2f}"),
]
for col, (label, val, sub) in zip([m1, m2, m3, m4, m5], cards):
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{val}</div>
            <div class='metric-sub'>{sub}</div>
            <div class='confidence-bar-bg'><div class='confidence-bar-fill' style='width:{float(val.strip("%"))}%'></div></div>
        </div>
        """, unsafe_allow_html=True)

# Linha de mercados extras
st.markdown("<br>", unsafe_allow_html=True)
e1, e2, e3, e4 = st.columns(4)
mercados = [
    ("+1.5 Gols", o15),
    ("+3.5 Gols", o35),
    ("Casa/Empate (1X)", p_c + p_e),
    ("Empate/Fora (X2)", p_e + p_f),
]
for col, (nome, prob) in zip([e1, e2, e3, e4], mercados):
    with col:
        st.markdown(f"""
        <div style='background:#111827;border:1px solid #1e293b;border-radius:8px;padding:10px 14px;text-align:center'>
            <div style='font-size:0.65rem;color:#94a3b8;font-family:JetBrains Mono,monospace;margin-bottom:4px'>{nome}</div>
            <div style='font-size:1.3rem;font-weight:700;font-family:Rajdhani,sans-serif;color:#3b82f6'>{prob:.1%}</div>
            <div style='font-size:0.65rem;color:#64748b'>Odd: {1/prob:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# SEÇÃO 3: GRÁFICOS
# -------------------------
st.markdown("---")
st.markdown('<div class="section-header">📈 ANÁLISE VISUAL</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎯 Mapa de Placares", "📊 Comparativo", "📉 Gols por Jogo"])

with tab1:
    # Heatmap de placares
    size = 6
    z = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            z[j][i] = poisson.pmf(i, exp_casa) * poisson.pmf(j, exp_fora) * 100

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=[str(i) for i in range(size)],
        y=[str(i) for i in range(size)],
        colorscale=[[0, '#0a0e1a'], [0.3, '#1d4ed8'], [0.6, '#00f5a0'], [1, '#fbbf24']],
        text=[[f"{z[j][i]:.1f}%" for i in range(size)] for j in range(size)],
        texttemplate="%{text}",
        textfont={"size": 10, "color": "white"},
        showscale=True,
        colorbar=dict(bgcolor='#111827', tickfont=dict(color='white'))
    ))
    fig.update_layout(
        title=dict(text=f"Probabilidade de Placares: {t_casa} (x) vs {t_fora} (y)", font=dict(color='white', size=13)),
        xaxis=dict(title=f"Gols {t_casa}", titlefont=dict(color='#94a3b8'), tickfont=dict(color='white'), gridcolor='#1e293b'),
        yaxis=dict(title=f"Gols {t_fora}", titlefont=dict(color='#94a3b8'), tickfont=dict(color='white'), gridcolor='#1e293b'),
        paper_bgcolor='#0a0e1a', plot_bgcolor='#111827', height=400,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Radar comparativo
    cats = ['Gols Marcados', 'Defesa Sólida', 'Aproveit.', 'Ataque Casa', 'Defesa Casa']
    
    def normalize(val, mx): return min(val / mx * 100 if mx else 0, 100)

    vals_c = [
        normalize(m_c_pro, 3),
        normalize(1/max(m_c_con, 0.1), 1/0.3),
        perc_c * 100,
        normalize(hc_gp, 3),
        normalize(1/max(hc_gc, 0.1), 1/0.3),
    ]
    vals_f = [
        normalize(m_f_pro, 3),
        normalize(1/max(m_f_con, 0.1), 1/0.3),
        perc_f * 100,
        normalize(hf_agp, 3),
        normalize(1/max(hf_agc, 0.1), 1/0.3),
    ]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatterpolar(r=vals_c + [vals_c[0]], theta=cats + [cats[0]], fill='toself',
        name=t_casa, line=dict(color='#00f5a0', width=2), fillcolor='rgba(0,245,160,0.15)'))
    fig2.add_trace(go.Scatterpolar(r=vals_f + [vals_f[0]], theta=cats + [cats[0]], fill='toself',
        name=t_fora, line=dict(color='#3b82f6', width=2), fillcolor='rgba(59,130,246,0.15)'))
    fig2.update_layout(
        polar=dict(
            bgcolor='#111827',
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color='#94a3b8'), gridcolor='#1e293b', linecolor='#1e293b'),
            angularaxis=dict(tickfont=dict(color='white'), linecolor='#1e293b')
        ),
        paper_bgcolor='#0a0e1a', legend=dict(font=dict(color='white'), bgcolor='#111827'),
        title=dict(text="Radar Comparativo", font=dict(color='white', size=13)),
        height=420
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    # Evolução de gols
    hist_all = pd.concat([hist_casa, hist_fora]).drop_duplicates().sort_values('Date')
    if len(hist_all) > 0:
        hist_all['TotalGols'] = hist_all['FTHG'] + hist_all['FTAG']
        hist_all['Match'] = hist_all['HomeTeam'] + " " + hist_all['FTHG'].astype(int).astype(str) + "x" + hist_all['FTAG'].astype(int).astype(str) + " " + hist_all['AwayTeam']
        hist_all_tail = hist_all.tail(20)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=list(range(len(hist_all_tail))),
            y=hist_all_tail['TotalGols'],
            marker=dict(
                color=hist_all_tail['TotalGols'],
                colorscale=[[0, '#1d4ed8'], [0.5, '#00f5a0'], [1, '#f97316']],
                showscale=False
            ),
            hovertext=hist_all_tail['Match'],
            hoverinfo='text+y'
        ))
        fig3.add_hline(y=2.5, line_dash="dash", line_color="#fbbf24", annotation_text="2.5 gols",
                      annotation_font_color="#fbbf24")
        fig3.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='white'), title="Gols na Partida", titlefont=dict(color='#94a3b8')),
            paper_bgcolor='#0a0e1a', plot_bgcolor='#111827',
            title=dict(text="Total de Gols — Últimos 20 Jogos Combinados", font=dict(color='white', size=13)),
            height=350, margin=dict(l=40, r=20, t=50, b=20)
        )
        st.plotly_chart(fig3, use_container_width=True)

# -------------------------
# SEÇÃO 4: SCANNER DE VALUE BETS
# -------------------------
st.markdown("---")
st.markdown('<div class="section-header">💰 SCANNER DE VALUE BETS</div>', unsafe_allow_html=True)

col_odds1, col_odds2 = st.columns([2, 1])

with col_odds1:
    st.markdown("**Insira as odds do mercado:**")
    o1, o2, o3 = st.columns(3)
    with o1: odd_casa = st.number_input(f"1 ({t_casa})", min_value=1.01, value=2.20, step=0.05, format="%.2f")
    with o2: odd_empate = st.number_input("X (Empate)", min_value=1.01, value=3.30, step=0.05, format="%.2f")
    with o3: odd_fora = st.number_input(f"2 ({t_fora})", min_value=1.01, value=3.10, step=0.05, format="%.2f")
    
    o4, o5 = st.columns(2)
    with o4: odd_btts = st.number_input("Ambos Marcam (S)", min_value=1.01, value=1.80, step=0.05, format="%.2f")
    with o5: odd_o25 = st.number_input("Over 2.5 Gols", min_value=1.01, value=2.00, step=0.05, format="%.2f")

mercado_scanner = [
    (f"Vitória {t_casa}", p_c, odd_casa),
    ("Empate", p_e, odd_empate),
    (f"Vitória {t_fora}", p_f, odd_fora),
    ("Ambos Marcam", btts, odd_btts),
    ("Over 2.5 Gols", o25, odd_o25),
]

with col_odds2:
    st.markdown("**Resumo de Apostas Sugeridas:**")
    for nome, prob, odd in mercado_scanner:
        ev = expected_value(prob, odd)
        stake, edge = kelly_criterion(prob, odd, banca, frac_kelly)
        if ev > 0.02:
            cor = "#4ade80"
            emoji = "🔥"
        elif ev > -0.02:
            cor = "#fbbf24"
            emoji = "⚠️"
        else:
            cor = "#f87171"
            emoji = "❌"
        st.markdown(f"""
        <div style='background:#111827;border:1px solid #1e293b;border-radius:6px;padding:8px 12px;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center'>
            <span style='font-size:0.78rem;font-family:Inter,sans-serif;color:#e2e8f0'>{emoji} {nome}</span>
            <span style='font-family:JetBrains Mono,monospace;font-size:0.72rem;color:{cor}'>EV: {ev:+.2f} | R${stake:.0f}</span>
        </div>
        """, unsafe_allow_html=True)

# Value bet principal
best = max(mercado_scanner, key=lambda x: expected_value(x[1], x[2]))
best_nome, best_prob, best_odd = best
best_ev = expected_value(best_prob, best_odd)
best_stake, _ = kelly_criterion(best_prob, best_odd, banca, frac_kelly)

st.markdown("<br>", unsafe_allow_html=True)
if best_ev > 0.03:
    st.markdown(f"""
    <div class='value-bet-card'>
        <div style='font-size:0.7rem;color:#4ade80;font-family:JetBrains Mono,monospace;letter-spacing:0.1em'>▶ MELHOR APOSTA IDENTIFICADA</div>
        <div style='font-size:1.4rem;font-weight:700;font-family:Rajdhani,sans-serif;color:white;margin:4px 0'>{best_nome} @ {best_odd:.2f}</div>
        <div style='display:flex;gap:20px;margin-top:6px'>
            <span style='font-size:0.75rem;color:#86efac'>Prob. Modelo: <b>{best_prob:.1%}</b></span>
            <span style='font-size:0.75rem;color:#86efac'>EV: <b>{best_ev:+.3f}</b></span>
            <span style='font-size:0.75rem;color:#86efac'>Kelly Stake: <b>R$ {best_stake:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class='no-value-card'>
        <div style='font-size:0.7rem;color:#fb923c;font-family:JetBrains Mono,monospace'>⚠ NENHUM VALUE MATEMÁTICO CLARO</div>
        <div style='font-size:0.85rem;color:#fed7aa;margin-top:4px'>Odds do mercado não apresentam vantagem esperada positiva. Considere outros mercados.</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# SEÇÃO 5: PLACARES + SCOUT
# -------------------------
st.markdown("---")
col_placares, col_scout = st.columns([1, 2])

with col_placares:
    st.markdown('<div class="section-header">🎯 PLACARES MAIS PROVÁVEIS</div>', unsafe_allow_html=True)
    for placar, prob in placares:
        h, a = map(int, placar.split('-'))
        if h > a: res_cor = "#4ade80"; res = "Casa"
        elif h == a: res_cor = "#fbbf24"; res = "Empate"
        else: res_cor = "#f87171"; res = "Fora"
        
        st.markdown(f"""
        <div style='background:#111827;border:1px solid #1e293b;border-radius:8px;padding:10px 16px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center'>
            <span style='font-family:Rajdhani,sans-serif;font-size:1.3rem;font-weight:700;color:white'>{placar}</span>
            <div style='text-align:right'>
                <div style='font-family:JetBrains Mono,monospace;font-size:0.85rem;color:{res_cor}'>{prob*100:.1f}%</div>
                <div style='font-size:0.65rem;color:#64748b'>{res}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_scout:
    st.markdown('<div class="section-header">🕵️ SCOUT DE JOGADORES</div>', unsafe_allow_html=True)
    setor = st.radio("Setor", ["Defesa", "Meio", "Ataque"], horizontal=True, label_visibility="collapsed")
    
    sc1, sc2 = st.columns(2)
    
    def render_scout_v2(team, setor, m_sofridos, m_pro, col):
        with col:
            st.markdown(f"<div style='font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:#3b82f6;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid #1e293b'>{team}</div>", unsafe_allow_html=True)
            jogadores = elencos.get(team, {}).get(setor, [f"Jogador {i}" for i in range(1,5)])
            
            np.random.seed(hash(team + setor) % (2**31))
            for j in jogadores:
                seed_val = hash(j) % 1000
                np.random.seed(seed_val)
                
                if setor == "Defesa":
                    desarmes = round((m_sofridos * 2.0) + np.random.uniform(0.5, 2.5), 1)
                    intercept = round(np.random.uniform(1.0, 3.5), 1)
                    passes = round(85 + np.random.uniform(-8, 12))
                    nota = round(min(10, 5 + perc_c * 3 + np.random.uniform(-0.5, 1.5)), 1)
                    stats = f"🛡️ {desarmes} des | ✂️ {intercept} int | 📊 {passes}% passes"
                elif setor == "Meio":
                    passes = round(88 + np.random.uniform(-10, 10))
                    key_passes = round(np.random.uniform(0.5, 3.0), 1)
                    tackles = round(np.random.uniform(1.0, 4.0), 1)
                    nota = round(min(10, 5 + np.random.uniform(0, 4)), 1)
                    stats = f"📈 {passes}% | 🔑 {key_passes} passes chave | ⚔️ {tackles} disps"
                else:
                    chutes = round((m_pro * 1.4) + np.random.uniform(0.5, 2.5), 1)
                    dribbles = round(np.random.uniform(0.5, 3.5), 1)
                    gols_90 = round(np.random.uniform(0.1, 0.6), 2)
                    nota = round(min(10, 5 + m_pro * 1.5 + np.random.uniform(-0.5, 1)), 1)
                    stats = f"🎯 {chutes} chutes | 🏃 {dribbles} drib | ⚽ {gols_90}/90"
                
                nota_cor = "#4ade80" if nota >= 7 else "#fbbf24" if nota >= 5.5 else "#f87171"
                st.markdown(f"""
                <div class='player-card'>
                    <div>
                        <div class='player-name'>{j}</div>
                        <div style='font-size:0.68rem;color:#94a3b8;font-family:JetBrains Mono,monospace;margin-top:3px'>{stats}</div>
                    </div>
                    <div style='text-align:center;min-width:40px'>
                        <div style='font-family:Rajdhani,sans-serif;font-size:1.2rem;font-weight:700;color:{nota_cor}'>{nota}</div>
                        <div style='font-size:0.6rem;color:#64748b'>nota</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    render_scout_v2(t_casa, setor, m_c_con, m_c_pro, sc1)
    render_scout_v2(t_fora, setor, m_f_con, m_f_pro, sc2)

# -------------------------
# SEÇÃO 6: HISTÓRICO
# -------------------------
st.markdown("---")
st.markdown('<div class="section-header">📋 HISTÓRICO RECENTE</div>', unsafe_allow_html=True)

# H2H
h2h = df[
    ((df['HomeTeam'] == t_casa) & (df['AwayTeam'] == t_fora)) |
    ((df['HomeTeam'] == t_fora) & (df['AwayTeam'] == t_casa))
].sort_values('Date', ascending=False)

tab_h1, tab_h2, tab_h3 = st.tabs([f"🆚 H2H ({len(h2h)} jogos)", f"🏠 {t_casa}", f"✈️ {t_fora}"])

def style_df(df_show):
    if df_show.empty:
        st.info("Sem dados históricos disponíveis.")
        return
    df_show = df_show[['Date', 'HomeTeam', 'FTHG', 'FTAG', 'AwayTeam']].copy()
    df_show.columns = ['Data', 'Casa', 'G.Casa', 'G.Fora', 'Fora']
    df_show['Resultado'] = df_show.apply(
        lambda r: f"{int(r['G.Casa'])} x {int(r['G.Fora'])}", axis=1
    )
    st.dataframe(
        df_show[['Data', 'Casa', 'Resultado', 'Fora']].head(10),
        use_container_width=True, hide_index=True
    )

with tab_h1: style_df(h2h)
with tab_h2: style_df(hist_casa.sort_values('Date', ascending=False))
with tab_h3: style_df(hist_fora.sort_values('Date', ascending=False))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-family:JetBrains Mono,monospace;font-size:0.65rem;color:#334155;padding:16px'>
    IA ELITE TERMINAL PRO v3.0 · Modelo Poisson + Critério de Kelly · Dados: football-data.co.uk<br>
    ⚠️ Finalidade analítica. Aposte com responsabilidade.
</div>
""", unsafe_allow_html=True)
