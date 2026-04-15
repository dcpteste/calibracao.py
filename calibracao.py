import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Sistemas Metrosul - Solo", page_icon="🏗️", layout="centered")

# --- FUNÇÃO DE AJUSTE AUTOMÁTICO ---
def ajustar_peso(valor):
    if 0 < valor < 30: # Se digitar em kg (ex: 4.5), vira gramas (4500)
        return valor * 1000
    return valor

# --- INICIALIZAÇÃO DA MEMÓRIA ---
if 'calib' not in st.session_state:
    st.session_state.calib = {
        "dens_areia": 1.450,
        "peso_cone": 1540.0,
        "vol_recipiente": 2120.0
    }

# --- FUNÇÃO PDF CALIBRAÇÃO ---
def gerar_pdf_calib(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "CERTIFICADO DE CALIBRACAO - AREIA", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " DADOS DA CALIBRACAO", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 8, " Volume do Recipiente (cm3):", border=1); pdf.cell(60, 8, f"{dados['vol']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Peso do Recipiente + Areia (g):", border=1); pdf.cell(60, 8, f"{dados['p_total']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Peso do Recipiente Vazio (g):", border=1); pdf.cell(60, 8, f"{dados['p_vazio']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Massa da Areia Calibrada (g):", border=1); pdf.cell(60, 8, f"{dados['massa_a']:.1f}", border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(190, 15, f" DENSIDADE DA AREIA: {dados['densidade']:.3f} g/cm3", border=1, ln=True, align='C', fill=True)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE POR ABAS ---
aba1, aba2 = st.tabs(["⚖️ Calibração da Areia", "🏗️ Ensaio de Campo"])

with aba1:
    st.header("Calibração da Densidade")
    st.write("Determine a massa específica da areia antes de ir para o campo.")
    
    with st.expander("1. Volume do Recipiente", expanded=True):
        st.write("Se não souber o volume, pese o recipiente com água (1g de água = 1cm³).")
        v_rec = st.number_input("Volume do Recipiente (cm³)", value=st.session_state.calib["vol_recipiente"], format="%.1f")
    
    with st.expander("2. Pesagem da Areia", expanded=True):
        c1, c2 = st.columns(2)
        p_vazio = c1.number_input("Peso Recipiente Vazio (g)", format="%.1f")
        p_cheio_raw = c2.number_input("Peso Recipiente + Areia (g)", format="%.1f")
        p_cheio = ajustar_peso(p_cheio_raw)
        
    if p_cheio > p_vazio:
        massa_a = p_cheio - p_vazio
        dens_a = massa_a / v_rec
        
        st.success(f"Densidade Calculada: **{dens_a:.3f} g/cm³**")
        
        if st.button("✅ Usar esta Densidade no Ensaio"):
            st.session_state.calib["dens_areia"] = dens_a
            st.session_state.calib["vol_recipiente"] = v_rec
            st.toast("Valor atualizado para o Ensaio!")
            
        dados_cal = {"vol": v_rec, "p_total": p_cheio, "p_vazio": p_vazio, "massa_a": massa_a, "densidade": dens_a}
        pdf_c = gerar_pdf_calib(dados_cal)
        st.download_button("📩 Baixar Certificado de Calibração", pdf_c, "Calibracao_Areia.pdf", "application/pdf")

with aba2:
    st.header("Ensaio de Frasco de Areia")
    # Aqui entraria o código que já fizemos, mas usando:
    # st.session_state.calib["dens_areia"] para o cálculo.
    st.write(f"Densidade Atual: **{st.session_state.calib['dens_areia']:.3f} g/cm³**")
    st.info("O cálculo do ensaio usará automaticamente o valor calibrado na primeira aba.")
