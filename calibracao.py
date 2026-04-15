import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Calibração de Areia | Metrosul", page_icon="⚖️")

# --- ESTILO ---
st.markdown("""<style>.stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #ddd; }</style>""", unsafe_allow_html=True)

# --- FUNÇÃO PDF ---
def gerar_pdf_calibracao(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "CALIBRACAO DA MASSA ESPECIFICA DA AREIA", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(5)

    # Tabela de Dados
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " DADOS DA AREIA E RECIPIENTE", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 8, " Massa do Recipiente + Areia (g):", border=1); pdf.cell(60, 8, f"{dados['p_total']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Massa do Recipiente Vazio (g):", border=1); pdf.cell(60, 8, f"{dados['p_vazio']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Massa da Areia (g):", border=1); pdf.cell(60, 8, f"{dados['p_areia']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Volume do Recipiente (cm3):", border=1); pdf.cell(60, 8, f"{dados['vol']:.1f}", border=1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(190, 15, f" DENSIDADE DA AREIA: {dados['densidade']:.3f} g/cm3", border=1, ln=True, align='C', fill=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("⚖️ Calibração da Areia")
st.info("Utilize este módulo para determinar a massa específica da areia de ensaio.")

with st.container():
    st.subheader("📏 Dados do Recipiente")
    col1, col2 = st.columns(2)
    # Volume do cilindro de calibração (geralmente você já sabe esse valor fixo)
    vol_recipiente = col1.number_input("Volume do Recipiente (cm³)", value=2120.0, format="%.1f")
    p_vazio = col2.number_input("Peso do Recipiente Vazio (g)", value=0.0, format="%.1f")

st.divider()

with st.container():
    st.subheader("⏳ Pesagem da Areia")
    # Digite o valor que deu na balança
    p_total = st.number_input("Peso do Recipiente + Areia (g)", format="%.1f", step=0.1)

# --- CÁLCULOS ---
if p_total > 0 and vol_recipiente > 0:
    massa_areia = p_total - p_vazio
    densidade_final = massa_areia / vol_recipiente
    
    st.divider()
    st.subheader("📊 Resultado da Calibração")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Massa Areia", f"{massa_areia:.1f} g")
    c2.metric("Volume", f"{vol_recipiente:.1f} cm³")
    c3.metric("DENSIDADE", f"{densidade_final:.3f}")

    dados_cal = {
        "p_total": p_total,
        "p_vazio": p_vazio,
        "p_areia": massa_areia,
        "vol": vol_recipiente,
        "densidade": densidade_final
    }
    
    pdf_cal = gerar_pdf_calibracao(dados_cal)
    st.download_button("📩 Gerar Certificado de Calibração", pdf_cal, "Calibracao_Areia.pdf", "application/pdf", use_container_width=True)

st.warning("⚠️ Lembre-se: A areia deve estar seca e limpa para uma calibração correta.")
