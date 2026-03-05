import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA ELITE TERMINAL PRO", layout="wide", page_icon="⚽")

st.markdown("""
<style>
.main {background:#f4f6fa;}
.stMetric {background:white;padding:12px;border-radius:10px;border:1px solid #ddd;}
.player-row {background:white;padding:8px;border-radius:6px;margin-bottom:5px;border-left:4px solid #2563eb;}
.label-time {font-weight:bold;font-size:18px;margin-bottom:8px;}
.value-box {padding:10px;border-radius:8px;margin-bottom:8px;}
.value-good {background:#dcfce7;}
.value-bad {background:#fee2e2;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# DATABASE SIMPLES DE ELENCOS (adicione mais se quiser)
# -------------------------
elencos = {
"Man City":{
"Defesa":["Gvardiol","Rúben Dias","Akanji","Rico Lewis"],
"Meio":["Rodri","Kovačić","Foden","Bernardo"],
"Ataque":["Haaland","Doku","Savinho","Alvarez"]
},
"Arsenal":{
"Defesa":["Saliba","Gabriel","White","Timber"],
"Meio":["Rice","Ødegaard","Havertz","Jorginho"],
"Ataque":["Saka","Martinelli","Trossard","Jesus"]
},
"Real Madrid":{
"Defesa":["Rüdiger","Militão","Carvajal","Mendy"],
"Meio":["Bellingham","Valverde","Camavinga","Tchouameni"],
"Ataque":["Vinicius","Mbappé","Rodrygo","Endrick"]
}
}

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data(ttl=7200)
def load_data(url):

    df = pd.read_csv(url,on_bad_lines="skip")

    df['Date'] = pd.to_datetime(df['Date'],dayfirst=True,errors="coerce").dt.date

    df = df.dropna(subset=['HomeTeam','AwayTeam','FTHG','FTAG'])

    return df


# -------------------------
# TEAM STATS
# -------------------------
def team_stats(df,team):

    jogos = df[(df['HomeTeam']==team)|(df['AwayTeam']==team)].tail(12)

    gols_pro = 0
    gols_con = 0

    forma = []

    for _,row in jogos.iterrows():

        if row['HomeTeam']==team:

            gols_pro += row['FTHG']
            gols_con += row['FTAG']

            if row['FTHG']>row['FTAG']:
                forma.append("🟢")
            elif row['FTHG']==row['FTAG']:
                forma.append("🟡")
            else:
                forma.append("🔴")

        else:

            gols_pro += row['FTAG']
            gols_con += row['FTHG']

            if row['FTAG']>row['FTHG']:
                forma.append("🟢")
            elif row['FTAG']==row['FTHG']:
                forma.append("🟡")
            else:
                forma.append("🔴")

    return gols_pro/len(jogos),gols_con/len(jogos),"".join(forma[-5:]),jogos


# -------------------------
# POISSON MODEL
# -------------------------
def poisson_model(exp_home,exp_away):

    p_home=p_draw=p_away=0
    btts=0
    o15=o25=o35=0

    scores={}

    for i in range(7):
        for j in range(7):

            prob = poisson.pmf(i,exp_home)*poisson.pmf(j,exp_away)

            scores[f"{i}-{j}"]=prob

            if i>j:
                p_home+=prob
            elif i==j:
                p_draw+=prob
            else:
                p_away+=prob

            if i>0 and j>0:
                btts+=prob

            if (i+j)>1.5:
                o15+=prob

            if (i+j)>2.5:
                o25+=prob

            if (i+j)>3.5:
                o35+=prob

    placares = sorted(scores.items(),key=lambda x:x[1],reverse=True)[:5]

    return p_home,p_draw,p_away,btts,o15,o25,o35,placares


# -------------------------
# MONTE CARLO
# -------------------------
def montecarlo(exp_home,exp_away):

    casa=emp=fora=0

    for _ in range(10000):

        g1=np.random.poisson(exp_home)
        g2=np.random.poisson(exp_away)

        if g1>g2:
            casa+=1
        elif g1==g2:
            emp+=1
        else:
            fora+=1

    return casa/10000,emp/10000,fora/10000


# -------------------------
# KELLY STAKE
# -------------------------
def kelly(prob,odd,banca,frac=0.5):

    k = ((odd*prob)-1)/(odd-1)

    if k<0:
        return 0

    return banca*k*frac


# -------------------------
# INTERFACE
# -------------------------

st.title("🛡️ IA ELITE FOOTBALL TERMINAL PRO")

liga = st.sidebar.selectbox("Liga",[
"Premier League (ING)",
"La Liga (ESP)",
"Serie A (ITA)",
"Série A (BRA)"
])

url_map={
"Premier League (ING)":"https://www.football-data.co.uk/mmz4281/2526/E0.csv",
"La Liga (ESP)":"https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
"Serie A (ITA)":"https://www.football-data.co.uk/mmz4281/2526/I1.csv",
"Série A (BRA)":"https://www.football-data.co.uk/mmz4281/2526/BRA.csv"
}

df = load_data(url_map[liga])

times = sorted(df['HomeTeam'].unique())

c1,c2 = st.columns(2)

with c1:
    t_casa = st.selectbox("Mandante",times)

with c2:
    t_fora = st.selectbox("Visitante",times,index=1)


# -------------------------
# STATS
# -------------------------
m_c_pro,m_c_con,forma_c,hist_casa = team_stats(df,t_casa)
m_f_pro,m_f_con,forma_f,hist_fora = team_stats(df,t_fora)

exp_casa = (m_c_pro+m_f_con)/2
exp_fora = (m_f_pro+m_c_con)/2


p_c,p_e,p_f,btts,o15,o25,o35,placares = poisson_model(exp_casa,exp_fora)

mc_c,mc_e,mc_f = montecarlo(exp_casa,exp_fora)


# -------------------------
# PROBABILIDADES
# -------------------------
st.subheader("📊 Probabilidades")

m1,m2,m3,m4 = st.columns(4)

m1.metric("Casa",f"{p_c:.1%}")
m2.metric("Empate",f"{p_e:.1%}")
m3.metric("Fora",f"{p_f:.1%}")
m4.metric("BTTS",f"{btts:.1%}")


# -------------------------
# MERCADOS DE GOLS
# -------------------------
st.subheader("⚽ Mercados de Gols")

g1,g2,g3 = st.columns(3)

g1.metric("Over 1.5",f"{o15:.1%}")
g2.metric("Over 2.5",f"{o25:.1%}")
g3.metric("Over 3.5",f"{o35:.1%}")


# -------------------------
# INSERIR ODDS
# -------------------------
st.subheader("💰 Inserir Odds do Mercado")

o1,o2,o3 = st.columns(3)

with o1:
    odd_home = st.number_input("Odd Casa",value=2.00)

with o2:
    odd_draw = st.number_input("Odd Empate",value=3.40)

with o3:
    odd_away = st.number_input("Odd Fora",value=3.50)

o4,o5 = st.columns(2)

with o4:
    odd_o25 = st.number_input("Odd Over 2.5",value=1.90)

with o5:
    odd_btts = st.number_input("Odd BTTS",value=1.85)


# -------------------------
# BANCA
# -------------------------
banca = st.number_input("💼 Banca Total",value=1000.0)


# -------------------------
# CALCULAR VALUE BETS
# -------------------------
st.subheader("🔥 Scanner de Value Bets")

bets = [
("Casa",p_c,odd_home),
("Empate",p_e,odd_draw),
("Fora",p_f,odd_away),
("Over 2.5",o25,odd_o25),
("BTTS",btts,odd_btts)
]

rows=[]

for nome,prob,odd in bets:

    odd_justa = 1/prob

    edge = (odd/odd_justa)-1

    ev = (prob*odd)-1

    stake = kelly(prob,odd,banca)

    rows.append({
    "Mercado":nome,
    "Probabilidade":round(prob,3),
    "Odd Mercado":odd,
    "Odd Justa":round(odd_justa,2),
    "Edge":round(edge*100,1),
    "EV":round(ev,3),
    "Stake Sugerida":round(stake,2)
    })


df_bets = pd.DataFrame(rows)

st.dataframe(df_bets,use_container_width=True)


# -------------------------
# PLACARES PROVÁVEIS
# -------------------------
st.subheader("🎯 Placares Prováveis")

st.dataframe(pd.DataFrame(placares,columns=["Placar","Probabilidade"]))


# -------------------------
# SCOUT JOGADORES
# -------------------------
st.subheader("🕵️ Scout de Jogadores")

setor = st.radio("Setor",["Defesa","Meio","Ataque"],horizontal=True)

cA,cB = st.columns(2)

def render(team,setor,g_sofridos,g_adv):

    st.markdown(f"<div class='label-time'>{team}</div>",unsafe_allow_html=True)

    if team in elencos:
        jogadores = elencos[team][setor]
    else:
        jogadores = ["Player 1","Player 2"]

    for j in jogadores:

        roubos = g_adv*2.4
        faltas = g_sofridos*1.7
        chutes = g_adv*1.3

        st.markdown(f"""
        <div class='player-row'>
        <b>{j}</b><br>
        🛡️ Desarmes: {roubos:.1f} |
        🚫 Faltas: {faltas:.1f} |
        🎯 Chutes: {chutes:.1f}
        </div>
        """,unsafe_allow_html=True)

with cA:
    render(t_casa,setor,m_c_con,m_f_pro)

with cB:
    render(t_fora,setor,m_f_con,m_c_pro)


# -------------------------
# HISTÓRICO
# -------------------------
st.subheader("📋 Últimos Jogos")

hist_total = pd.concat([hist_casa,hist_fora]).drop_duplicates().sort_values(by='Date',ascending=False)

hist_view = hist_total[['Date','HomeTeam','AwayTeam','FTHG','FTAG']]

hist_view.columns=['Data','Mandante','Visitante','Gols Casa','Gols Fora']

st.dataframe(hist_view,use_container_width=True)
