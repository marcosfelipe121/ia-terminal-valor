import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="IA ELITE TERMINAL PRO", layout="wide", page_icon="⚽")

# --- ESTILIZAÇÃO CSS (Mantida) ---
st.markdown("""
<style>
.main {background:#f4f6fa;}
.stMetric {background:white;padding:12px;border-radius:10px;border:1px solid #ddd;}
.player-row {background:white;padding:8px;border-radius:6px;margin-bottom:5px;border-left:4px solid #2563eb; font-size: 13px;}
.label-time {font-weight:bold;font-size:18px;margin-bottom:8px; color: #1e40af; border-bottom: 2px solid #eee;}
</style>
""", unsafe_allow_html=True)

# --- DATABASE DE ELENCOS (Corrigida para evitar erros de busca) ---
elencos = {
    "Man City": {"Defesa": ["Akanji", "Dias", "Gvardiol", "Walker"], "Meio": ["Rodri", "De Bruyne", "Foden", "Bernardo"], "Ataque": ["Haaland", "Doku", "Savinho", "Grealish"]},
    "Arsenal": {"Defesa": ["Saliba", "Gabriel", "White", "Timber"], "Meio": ["Rice", "Odegaard", "Havertz", "Merino"], "Ataque": ["Saka", "Martinelli", "Trossard", "Jesus"]},
    "Liverpool": {"Defesa": ["Van Dijk", "Konate", "Trent AA", "Robertson"], "Meio": ["Mac Allister", "Szoboszlai", "Gravenberch", "Jones"], "Ataque": ["Salah", "Diaz", "Nunez", "Jota"]},
    "Real Madrid": {"Defesa": ["Rüdiger", "Militão", "Carvajal", "Mendy"], "Meio": ["Bellingham", "Valverde", "Tchouaméni", "Camavinga"], "Ataque": ["Vinícius Jr", "Mbappé", "Rodrygo", "Endrick"]},
    "Barcelona": {"Defesa": ["Cubarsí", "Iñigo", "Koundé", "Balde"], "Meio": ["Pedri", "Casadó", "Olmo", "De Jong"], "Ataque": ["Lewandowski", "Yamal", "Raphinha", "Ferran"]},
    # Adicione os outros times conforme necessário...
}

# --- FUNÇÕES DE CÁLCULO ---
@st.cache_data(ttl=7200)
def load_data(url):
    try:
        # Adicionado encoding para evitar erro em caracteres especiais
        df = pd.read_csv(url, encoding='utf-8', on_bad_lines="skip")
        
        # Correção na conversão de data
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors="coerce")
        
        # Remove linhas onde os placares são nulos
        df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
        return df
    except Exception as e:
        # Se falhar o utf-8, tenta latin-1 (comum em arquivos de futebol)
        try:
            df = pd.read_csv(url, encoding='latin-1', on_bad_lines="skip")
            return df
        except:
            st.error(f"Erro crítico ao carregar dados: {e}")
            return pd.DataFrame()

def team_stats(df, team):
    # Filtra jogos do time (Mandante ou Visitante)
    jogos = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].sort_values('Date', ascending=True).tail(12)
    
    if len(jogos) == 0: 
        return 0, 0, "N/A", jogos
    
    g_pro = 0
    g_con = 0
    forma = []
    
    for _, row in jogos.iterrows():
        if row['HomeTeam'] == team:
            gp, gc = row['FTHG'], row['FTAG']
        else:
            gp, gc = row['FTAG'], row['FTHG']
            
        g_pro += gp
        g_con += gc
        res = "🟢" if gp > gc else "🟡" if gp == gc else "🔴"
        forma.append(res)
    
    media_pro = g_pro / len(jogos)
    media_con = g_con / len(jogos)
    return media_pro, media_con, "".join(forma[-5:]), jogos

# ... (Mantenha as funções poisson_model e kelly como estão)
