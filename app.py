import streamlit as st
import pandas as pd

# 1. Configuração visual
st.set_page_config(page_title="Copa Renegados - Vôlei", layout="centered")

# --- CONFIGURAÇÃO DAS CHAVES ---
CONFIG_TIMES = {
    "Moving": {"chave": "A", "escudo": "Logos/moving.png"},
    "Ultravolei A": {"chave": "A", "escudo": "Logos/ultraa.png"},
    "Winx Pride": {"chave": "A", "escudo": "Logos/winx.png"},
    "Ultravolei B": {"chave": "B", "escudo": "Logos/ultrab.png"},
    "MSC Voleibol": {"chave": "B", "escudo": "Logos/msc.png"},
    "Vetera": {"chave": "B", "escudo": "Logos/vetera.png"},
}

# --- 2. CONEXÃO COM GOOGLE SHEETS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1TDh3etg71hvZcGRgpusY_9ZEw9d6I9rojB9eVE4wYJ8/export?format=csv"

try:
    df_jogos = pd.read_csv(URL_PLANILHA)
    df_jogos = df_jogos.fillna("") 
    jogos_fase_grupos = df_jogos.values.tolist()
except Exception as e:
    st.error(f"Erro ao ler a planilha: {e}")
    jogos_fase_grupos = []

def parse_linha(linha):
    hora = str(linha[0]).strip()
    fase = str(linha[1]).strip().upper() 
    t1 = str(linha[2]).strip()
    s1 = int(float(str(linha[3]))) if str(linha[3]).strip() else 0
    s2 = int(float(str(linha[4]))) if str(linha[4]).strip() else 0
    t2 = str(linha[5]).strip()
    return hora, fase, t1, s1, s2, t2

# --- LÓGICA DE CÁLCULO ---
def calcular_tabela(lista_jogos):
    resumo = {nome: {"Pts": 0, "J": 0, "V": 0, "D": 0, "SP": 0, "SC": 0, "SA": 0} for nome in CONFIG_TIMES}
    
    for linha in lista_jogos:
        if len(linha) < 6: continue 
        hora, fase, t1, s1, s2, t2 = parse_linha(linha)
        
        if not fase.startswith("CHAVE"): continue
        if t1 not in resumo or t2 not in resumo: continue
        if s1 == 0 and s2 == 0: continue 
        
        resumo[t1]["J"] += 1; resumo[t2]["J"] += 1
        resumo[t1]["SP"] += s1; resumo[t1]["SC"] += s2
        resumo[t2]["SP"] += s2; resumo[t2]["SC"] += s1
        
        if s1 == 2 and s2 == 0:
            resumo[t1]["Pts"] += 3; resumo[t1]["V"] += 1; resumo[t2]["D"] += 1
        elif s1 == 2 and s2 == 1:
            resumo[t1]["Pts"] += 2; resumo[t2]["Pts"] += 1; resumo[t1]["V"] += 1; resumo[t2]["D"] += 1
        elif s1 == 1 and s2 == 2:
            resumo[t1]["Pts"] += 1; resumo[t2]["Pts"] += 2; resumo[t2]["V"] += 1; resumo[t1]["D"] += 1
        elif s1 == 0 and s2 == 2:
            resumo[t2]["Pts"] += 3; resumo[t2]["V"] += 1; resumo[t1]["D"] += 1
                
    for t in resumo:
        resumo[t]["SA"] = resumo[t]["SP"] - resumo[t]["SC"]
        
    return resumo

# --- INTERFACE ---
st.title("🦊 Copa Renegados Vôlei")

# --- LINK DO INSTAGRAM ---
st.info("📸 **Acompanhe os bastidores e jogos!** Veja nossos stories no Instagram: [@renegadosvolleybol](https://instagram.com/renegadosvolleybol)")

dados_tabela = calcular_tabela(jogos_fase_grupos)

def mostrar_chave(letra):
    st.subheader(f"Chave {letra}")
    times_da_chave = [t for t, info in CONFIG_TIMES.items() if info["chave"] == letra]
    info_chave = {t: dados_tabela[t] for t in times_da_chave}
    
    df = pd.DataFrame.from_dict(info_chave, orient='index')
    df = df.sort_values(by=["Pts", "SA", "SP"], ascending=False)
    st.table(df)

col1, col2 = st.columns(2)
with col1:
    mostrar_chave("A")
with col2:
    mostrar_chave("B")

st.caption("🔍 **Legenda:** **Pts** = Pontos | **J** = Jogos | **V** = Vitórias | **D** = Derrotas | **SP** = Sets Pró | **SC** = Sets Contra | **SA** = Saldo")
st.divider()

# --- RESULTADOS DOS JOGOS ---
with st.expander("📅 Ver Placar de Todos os Jogos", expanded=False):
    for linha in jogos_fase_grupos:
        if len(linha) < 6: continue
        hora, fase, t1, s1, s2, t2 = parse_linha(linha)
        
        if t1 not in CONFIG_TIMES or t2 not in CONFIG_TIMES: continue

        st.markdown(f"<p style='text-align: center; color: gray; font-size: 12px; margin-bottom: 0px;'>{hora} - {fase}</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 3])
        
        with c1:
            st.image(CONFIG_TIMES[t1]["escudo"], width=30)
            st.write(f"**{t1}**")
        with c2:
            if s1 == 0 and s2 == 0:
                st.markdown("<h4 style='text-align: center;'>🆚</h4>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h4 style='text-align: center;'>{s1} x {s2}</h4>", unsafe_allow_html=True)
        with c3:
            st.image(CONFIG_TIMES[t2]["escudo"], width=30)
            st.write(f"**{t2}**")
        st.divider()

# --- FASE FINAL ---
st.header("🏆 Fase Final")

def get_jogo_fase(nome_fase):
    for linha in jogos_fase_grupos:
        if len(linha) < 6: continue
        hora, fase, t1, s1, s2, t2 = parse_linha(linha)
        if fase == nome_fase.upper():
            return t1, s1, s2, t2
    return "", 0, 0, ""

s1_t1, s1_p1, s1_p2, s1_t2 = get_jogo_fase("SEMI 1")
s2_t1, s2_p1, s2_p2, s2_t2 = get_jogo_fase("SEMI 2")
f_t1, f_p1, f_p2, f_t2 = get_jogo_fase("1 E 2º LUGAR")
t3_t1, t3_p1, t3_p2, t3_t2 = get_jogo_fase("3º LUGAR")

def render_match(titulo, p1, p2, t1, t2):
    st.write(f"**{titulo}**")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if t1 in CONFIG_TIMES:
            st.image(CONFIG_TIMES[t1]["escudo"], width=40)
            st.caption(t1)
        else:
            st.markdown("<h3 style='text-align: center;'>🛡️</h3>", unsafe_allow_html=True)
            st.caption("A definir")
            
    with c2:
        if p1 == 0 and p2 == 0:
            st.markdown("<h4 style='text-align: center; margin-top: 10px;'>🆚</h4>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h4 style='text-align: center; margin-top: 10px;'>{p1} x {p2}</h4>", unsafe_allow_html=True)
            
    with c3:
        if t2 in CONFIG_TIMES:
            st.image(CONFIG_TIMES[t2]["escudo"], width=40)
            st.caption(t2)
        else:
            st.markdown("<h3 style='text-align: center;'>🛡️</h3>", unsafe_allow_html=True)
            st.caption("A definir")

# Layout mais limpo e na ordem exata solicitada
col_s1, col_s2 = st.columns(2)
with col_s1:
    render_match("SEMI 1", s1_p1, s1_p2, s1_t1, s1_t2)
with col_s2:
    render_match("SEMI 2", s2_p1, s2_p2, s2_t1, s2_t2)

st.divider()

col_3o, col_final = st.columns(2)
with col_3o:
    render_match("🥉 3º LUGAR", t3_p1, t3_p2, t3_t1, t3_t2)
with col_final:
    render_match("🥇 GRANDE FINAL", f_p1, f_p2, f_t1, f_t2)

# Confetes para o Campeão!
if f_p1 > f_p2:
    st.success(f"🏆 O grande campeão é o **{f_t1}**!")
    st.balloons()
elif f_p2 > f_p1:
    st.success(f"🏆 O grande campeão é o **{f_t2}**!")
    st.balloons()