import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="IA TERMINAL ELITE", layout="wide", page_icon="🔥")

def prever_mercado(m_casa, m_fora, tipo="gols"):
    # Poisson Matrix para Gols ou Cantos
    p_casa = p_empate = p_fora = 0
    over_base = 2.5 if tipo == "gols" else 9.5
    prob_over = 0
    
    for i in range(15):
        for j in range(15):
            prob = poisson.pmf(i, m_casa) * poisson.pmf(j, m_fora)
            if i > j: p_casa += prob
            elif i == j: p_empate += prob
            else: p_fora += prob
            if (i + j) > over_base: prob_over += prob
    return p_casa, p_empate, p_fora, prob_over

st.title("🔥 IA Terminal Elite: Operação Profissional")
st.subheader("Foco: Dados de Hoje, Gols e Escanteios")

# --- ÁREA DE ENTRADA RÁPIDA ---
with st.container():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        jogo = st.text_input("Confronto (Ex: Tottenham x Man City)", "Jogo de Hoje")
    with col2:
        banca = st.number_input("Saldo Banca (R$)", value=1000.0)
    with col3:
        kelly_pct = st.slider("Agressividade (%)", 1, 100, 25) / 100

st.divider()

# --- INPUTS TÉCNICOS ---
c1, c2 = st.columns(2)

with c1:
    st.markdown("### ⚽ Médias de Gols (Últimos 5-10 jogos)")
    mg_c = st.number_input("Casa Gols Pró", value=1.7)
    mg_f = st.number_input("Fora Gols Pró", value=1.3)
    odd_gols = st.number_input("Odd Over 2.5 Gols", value=1.85)

with c2:
    st.markdown("### ⛳ Médias de Cantos (Últimos 5-10 jogos)")
    mc_c = st.number_input("Casa Cantos Pró", value=6.2)
    mc_f = st.number_input("Fora Cantos Pró", value=5.1)
    odd_cantos = st.number_input("Odd Over 9.5 Cantos", value=1.90)

# --- PROCESSAMENTO ---
if st.button("⚡ GERAR ANÁLISE DE VALOR"):
    # Cálculos
    pg_c, pg_e, pg_f, pg_o25 = prever_mercado(mg_c, mg_f, "gols")
    pc_c, pc_e, pc_f, pc_o95 = prever_mercado(mc_c, mc_f, "cantos")
    
    st.divider()
    
    # Exibição Gols
    res_g1, res_g2 = st.columns(2)
    with res_g1:
        st.info(f"📊 Probabilidade Over 2.5 Gols: **{pg_o25:.1%}**")
        ev_g = (pg_o25 * odd_gols) - 1
        if ev_g > 0:
            stake = ((pg_o25 * (odd_gols - 1)) - (1 - pg_o25)) / (odd_gols - 1) * banca * kelly_pct
            st.success(f"💎 VALOR! EV: {ev_g:.1%} | Sugestão: R$ {max(0, stake):.2f}")
        else:
            st.error(f"❌ SEM VALOR (EV: {ev_g:.1%})")

    # Exibição Cantos
    with res_g2:
        st.info(f"⛳ Probabilidade Over 9.5 Cantos: **{pc_o95:.1%}**")
        ev_c = (pc_o95 * odd_cantos) - 1
        if ev_c > 0:
            stake_c = ((pc_o95 * (odd_cantos - 1)) - (1 - pc_o95)) / (odd_cantos - 1) * banca * kelly_pct
            st.success(f"💎 VALOR! EV: {ev_c:.1%} | Sugestão: R$ {max(0, stake_c):.2f}")
        else:
            st.error(f"❌ SEM VALOR (EV: {ev_c:.1%})")

    # Placar Provável (O toque de mestre)
    st.divider()
    st.markdown(f"🎯 **Placar Mais Provável:** {round(mg_c)} x {round(mg_f)} | **Cantos Estimados:** {mc_c + mc_f:.1f}")
