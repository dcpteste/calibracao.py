import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Sistemas Metrosul - Solo", page_icon="🏗️", layout="centered")

# --- FUNÇÃO DE AJUSTE AUTOMÁTICO (KG para G) ---
def ajustar_peso(valor):
    if 0 < valor < 30:
        return valor * 1000
    return valor

# --- INICIALIZAÇÃO DA MEMÓRIA (Session State) ---
if 'calib' not in st.session_state:
    st.session_state.calib = {
        "dens_areia": 1.450,
        "peso_cone": 1540.0,
        "vol_recipiente": 2120.0,
        "proctor_max": 2.050,
        "limite_gc": 95.0
    }

# --- FUNÇÃO PARA GERAR PDF (FORMATO TÉCNICO) ---
def gerar_pdf_ensaio(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "RELATORIO DE ENSAIO - FRASCO DE AREIA", ln=True, align='C')
    pdf.set_font("Arial", "I", 9)
    pdf.cell(200, 5, "Norma DNER-ME 092/94", ln=True, align='C')
    pdf.ln(5)

    sections = [
        ("1. IDENTIFICACAO", [f"OS: {dados['os']}", f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", f"Local: {dados['endereco']}"]),
        ("2. UMIDADE", [f"Solo Umido+B: {dados['p_bu']:.1f}g", f"Solo Seco+B: {dados['p_bs']:.1f}g", f"UMIDADE: {dados['umidade']:.2f} %"]),
        ("3. PESOS E VOLUMES", [f"Areia na Cava: {dados['p_areia_cava']:.1f}g", f"Volume Cava: {dados['vol']:.1f} cm3", f"Solo Umido Cava: {dados['p_solo_real']:.1f}g"]),
        ("4. CONCLUSAO", [f"Dens. Seca: {dados['dens_seca']:.3f} g/cm3", f"Proctor Lab: {dados['proctor']:.3f} g/cm3"])
    ]

    for title, lines in sections:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 7, f" {title}", border=1, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        for line in lines:
            pdf.cell(190, 8, f" {line}", border=1, ln=True)
        pdf.ln(2)

    pdf.ln(5)
    color = (0, 100, 0) if dados['gc'] >= dados['limite'] else (200, 0, 0)
    pdf.set_text_color(*color)
    pdf.set_font("Arial", "B", 14)
    status_txt = "APROVADO" if dados['gc'] >= dados['limite'] else "RECOMPACTAR"
    pdf.cell(190, 15, f" GRAU DE COMPACTACAO: {dados['gc']:.1f} %", border=1, ln=True, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"STATUS: {status_txt}", border=0, ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE PRINCIPAL ---
st.title("🏗️ Controle de Solo - Metrosul")

aba1, aba2 = st.tabs(["⚖️ Calibração da Areia", "🧪 Ensaio de Campo"])

# --- ABA 1: CALIBRAÇÃO ---
with aba1:
    st.header("Calibração da Densidade")
    col1, col2 = st.columns(2)
    v_rec = col1.number_input("Volume do Recipiente (cm³)", value=st.session_state.calib["vol_recipiente"])
    p_cone_fixo = col2.number_input("Peso no Cone (g)", value=st.session_state.calib["peso_cone"])
    
    st.divider()
    c1, c2 = st.columns(2)
    p_v = c1.number_input("Peso Recipiente Vazio (g)", key="pv_cal")
    p_c_raw = c2.number_input("Peso Recipiente + Areia (g)", key="pc_cal")
    p_c = ajustar_peso(p_c_raw)
    
    if p_c > p_v:
        m_areia = p_c - p_v
        d_calculada = m_areia / v_rec
        st.metric("Densidade Encontrada", f"{d_calculada:.3f} g/cm³")
        
        if st.button("💾 Salvar e Usar no Ensaio", use_container_width=True):
            st.session_state.calib.update({"dens_areia": d_calculada, "vol_recipiente": v_rec, "peso_cone": p_cone_fixo})
            st.success("Configurações atualizadas para o Ensaio!")

# --- ABA 2: ENSAIO DE CAMPO ---
with aba2:
    st.header("Ensaio de Frasco de Areia")
    
    with st.expander("📝 Dados de Identificação", expanded=True):
        os = st.text_input("Número da OS")
        loc = st.text_input("Local / Estaca")
    
    col_u, col_s = st.columns(2)
    with col_u:
        st.subheader("🔥 Umidade")
        bu = ajustar_peso(st.number_input("Bandeja + Solo Úmido", key="bu_e"))
        bs = ajustar_peso(st.number_input("Bandeja + Solo Seco", key="bs_e"))
        t_u = st.number_input("Tara Bandeja (g)", value=100.0)
        umid = ((bu - bs) / (bs - t_u)) * 100 if (bs - t_u) > 0 else 0.0
        st.caption(f"Umidade: {umid:.2f}%")

    with col_s:
        st.subheader("🕳️ Solo da Cava")
        p_t = ajustar_peso(st.number_input("Total (Solo+Bandeja)", key="pt_e"))
        t_c = st.number_input("Tara Bandeja Cava", value=500.0)
        p_solo = p_t - t_c
        st.caption(f"Solo Líquido: {p_solo:.1f}g")

    st.subheader("⚖️ Pesagem do Frasco")
    f1, f2 = st.columns(2)
    pi = ajustar_peso(f1.number_input("Peso Inicial Frasco", key="pi_e"))
    pf = ajustar_peso(f2.number
