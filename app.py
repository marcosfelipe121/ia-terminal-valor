import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA ELITE PREDICTOR PRO", layout="wide", page_icon="⚽")

st.markdown("""
<style>
.main {background-color:#f4f6fa;}
.stMetric {background:white;padding:12px;border-radius:10px;border:1px solid #ddd;}
h1,h2,h3 {color:#1e3a8a;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data(ttl=7200)
def load_data(url):

    df = pd.read_csv(url, on_bad_lines='skip')

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date

    df = df.dropna(subset=['HomeTeam','AwayTeam','FTHG','FTAG'])

    return df


# -----------------------------
# TEAM STATS
# -----------------------------

def team_stats(df, team):

    jogos = df[(df['HomeTeam']==team)|(df['AwayTeam']==team)].tail(12)

    g_pro = 0
    g_con = 0

    resultados = []

    for _,row in jogos.iterrows():

        if row['HomeTeam']==team:
            g_pro += row['FTHG']
            g_con += row['FTAG']

            if row['FTHG']>row['FTAG']:
                resultados.append("🟢")
            elif row['FTHG']==row['FTAG']:
                resultados.append("🟡")
            else:
                resultados.append("🔴")

        else:
            g_pro += row['FTAG']
            g_con += row['FTHG']

            if row['FTAG']>row['FTHG']:
                resultados.append("🟢")
            elif row['FTAG']==row['FTHG']:
                resultados.append("🟡")
            else:
                resultados.append("🔴")

    media_pro = g_pro/len(jogos)
    media_con = g_con/len(jogos)

    forma5 = "".join(resultados[-5:])
    forma10 = "".join(resultados[-10:])

    return media_pro,media_con,forma5,forma10,jogos


# -----------------------------
# POISSON MODEL
# -----------------------------

def poisson_model(exp_home,exp_away):

    p_home=p_draw=p_away=0
    btts=0
    o05=o15=o25=o35=0

    score_probs={}

    for i in range(8):
        for j in range(8):

            prob = poisson.pmf(i,exp_home)*poisson.pmf(j,exp_away)

            score_probs[f"{i}-{j}"]=prob

            if i>j:
                p_home+=prob
            elif i==j:
                p_draw+=prob
            else:
                p_away+=prob

            if i>0 and j>0:
                btts+=prob

            if (i+j)>0.5:
                o05+=prob

            if (i+j)>1.5:
                o15+=prob

            if (i+j)>2.5:
                o25+=prob

            if (i+j)>3.5:
                o35+=prob

    top_scores = sorted(score_probs.items(),key=lambda x:x[1],reverse=True)[:5]

    return p_home,p_draw,p_away,btts,o05,o15,o25,o35,top_scores


# -----------------------------
# MONTE CARLO
# -----------------------------

def montecarlo(exp_home,exp_away,sim=10000):

    casa=emp=fora=0

    for _ in range(sim):

        g1=np.random.poisson(exp_home)
        g2=np.random.poisson(exp_away)

        if g1>g2:
            casa+=1
        elif g1==g2:
            emp+=1
        else:
            fora+=1

    return casa/sim,emp/sim,fora/sim


# -----------------------------
# INTERFACE
# -----------------------------

st.title("🛡️ IA ELITE FOOTBALL TERMINAL")

liga = st.sidebar.selectbox("Competição",[
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

df=load_data(url_map[liga])

times=sorted(df['HomeTeam'].unique())

col1,col2=st.columns(2)

with col1:
    t_casa=st.selectbox("Mandante",times)

with col2:
    t_fora=st.selectbox("Visitante",times,index=1)

# -----------------------------
# STATS
# -----------------------------

m_c_pro,m_c_con,forma5_c,forma10_c,hist_casa = team_stats(df,t_casa)
m_f_pro,m_f_con,forma5_f,forma10_f,hist_fora = team_stats(df,t_fora)

exp_casa=(m_c_pro+m_f_con)/2
exp_fora=(m_f_pro+m_c_con)/2

# -----------------------------
# POISSON
# -----------------------------

p_c,p_e,p_f,btts,o05,o15,o25,o35,placares = poisson_model(exp_casa,exp_fora)

# -----------------------------
# MONTECARLO
# -----------------------------

mc_c,mc_e,mc_f = montecarlo(exp_casa,exp_fora)

# -----------------------------
# MÉTRICAS PRINCIPAIS
# -----------------------------

st.subheader("📊 Probabilidades")

m1,m2,m3,m4=st.columns(4)

m1.metric("Casa",f"{p_c:.1%}")
m2.metric("Empate",f"{p_e:.1%}")
m3.metric("Fora",f"{p_f:.1%}")
m4.metric("BTTS",f"{btts:.1%}")

# -----------------------------
# OVER MARKETS
# -----------------------------

st.subheader("⚽ Mercados de Gols")

g1,g2,g3,g4=st.columns(4)

g1.metric("Over 0.5",f"{o05:.1%}")
g2.metric("Over 1.5",f"{o15:.1%}")
g3.metric("Over 2.5",f"{o25:.1%}")
g4.metric("Over 3.5",f"{o35:.1%}")

# -----------------------------
# ODDS JUSTAS
# -----------------------------

st.subheader("💰 Odds Justas")

odd_c=1/p_c
odd_e=1/p_e
odd_f=1/p_f

df_odds=pd.DataFrame({
"Mercado":["Casa","Empate","Fora"],
"Probabilidade":[p_c,p_e,p_f],
"Odd Justa":[odd_c,odd_e,odd_f]
})

st.dataframe(df_odds,use_container_width=True)

# -----------------------------
# VALUE BET
# -----------------------------

st.subheader("🔥 Value Bet Detector")

odd_input=st.number_input("Odd Mercado",value=1.80)

prob_input=o25

ev=(prob_input*odd_input)-1

if ev>0:
    st.success(f"VALUE BET | EV = {ev:.2f}")
else:
    st.error(f"Sem valor | EV = {ev:.2f}")

# -----------------------------
# PLACARES
# -----------------------------

st.subheader("🎯 Placares Mais Prováveis")

plac_df=pd.DataFrame(placares,columns=["Placar","Probabilidade"])

st.dataframe(plac_df,use_container_width=True)

# -----------------------------
# MONTECARLO
# -----------------------------

st.subheader("🧠 Simulação Monte Carlo")

mc_df=pd.DataFrame({
"Resultado":["Casa","Empate","Fora"],
"Probabilidade":[mc_c,mc_e,mc_f]
})

st.dataframe(mc_df,use_container_width=True)

# -----------------------------
# FORMA
# -----------------------------

st.subheader("📈 Forma Recente")

f1,f2=st.columns(2)

with f1:
    st.write(f"**{t_casa}**")
    st.write("Últimos 5:",forma5_c)
    st.write("Últimos 10:",forma10_c)

with f2:
    st.write(f"**{t_fora}**")
    st.write("Últimos 5:",forma5_f)
    st.write("Últimos 10:",forma10_f)

# -----------------------------
# HISTÓRICO
# -----------------------------

st.subheader("📋 Últimos Jogos")

hist_total=pd.concat([hist_casa,hist_fora]).drop_duplicates().sort_values(by='Date',ascending=False)

hist_view=hist_total[['Date','HomeTeam','AwayTeam','FTHG','FTAG']]

hist_view.columns=['Data','Mandante','Visitante','Gols Casa','Gols Fora']

st.dataframe(hist_view,use_container_width=True,hide_index=True)
