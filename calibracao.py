import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Calibração de Areia | Metrosul", page_icon="⚖️", layout="centered")

# --- FUNÇÃO DE AJUSTE AUTOMÁTICO (KG para G) ---
def ajustar_peso(valor):
    if 0 < valor < 30:
        return valor * 1000
    return valor

# --- FUNÇÃO PARA GERAR PDF DE CALIBRAÇÃO ---
def gerar_pdf_calib(dados):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "CERTIFICADO DE CALIBRACAO DA AREIA", ln=True, align='C')
    pdf.set_font("Arial", "I", 9)
    pdf.cell(200, 5, "Determinação da Massa Específica Aparente", ln=True, align='C')
    pdf.ln(10)

    # Tabela de Dados
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(190, 8, " DADOS DA MEDICAO", border=1, ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(130, 8, " Volume do Recipiente (cm³):", border=1); pdf.cell(60, 8, f"{dados['vol']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Peso do Recipiente + Areia (g):", border=1); pdf.cell(60, 8, f"{dados['p_total']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Peso do Recipiente Vazio (g):", border=1); pdf.cell(60, 8, f"{dados['p_vazio']:.1f}", border=1, ln=True)
    pdf.cell(130, 8, " Densidade da Areia (g/m³):", border=1); pdf.cell(60, 8, f"{dados['massa_a']:.1f}", border=1, ln=True)
    
    pdf.ln(10)
    
    # Resultado Final de Destaque
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(190, 15, f" DENSIDADE DA AREIA: {dados['densidade']:.3f} g/cm3", border=1, ln=True, align='C', fill=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 5, f"Calibracao realizada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
st.title("⚖️ Calibração de Areia")
st.caption("Ambiental Metrosul - Laboratório de Solos")

with st.container():
    st.subheader("📏 1. Volume do Recipiente")
    st.info("O volume padrão costuma ser 2120 cm³, mas confira o seu cilindro.")
    vol_recipiente = st.number_input("Volume do Recipiente (cm³)", value=2120.0, format="%.1f")

st.divider()

with st.container():
    st.subheader("⏳ 2. Pesagens")
    c1, c2 = st.columns(2)
    p_vazio = c1.number_input("Peso do Recipiente Vazio (g)", format="%.1f")
    p_total_raw = c2.number_input("Peso Recipiente + Areia (g)", format="%.1f")
    p_total = ajustar_peso(p_total_raw)

# --- CÁLCULO ---
if p_total > p_vazio and vol_recipiente > 0:
    massa_areia = p_total - p_vazio
    densidade_final = massa_areia / vol_recipiente
    
    st.divider()
    st.subheader("📊 Resultado Final")
    
    res1, res2 = st.columns(2)
    res1.metric("Massa da Areia", f"{massa_areia:.1f} g")
    res2.metric("DENSIDADE", f"{densidade_final:.3f} g/cm³")

    # Preparar Dados para o PDF
    dados_cal = {
        "vol": vol_recipiente,
        "p_total": p_total,
        "p_vazio": p_vazio,
        "massa_a": massa_areia,
        "densidade": densidade_final
    }
    
    pdf_bytes = gerar_pdf_calib(dados_cal)
    
    st.download_button(
        label="📥 Baixar Certificado de Calibração",
        data=pdf_bytes,
        file_name=f"Calibracao_Areia_{datetime.now().strftime('%d%m%Y')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.sidebar.markdown("### Instruções")
st.sidebar.write("1. Verifique se o recipiente está limpo.")
st.sidebar.write("2. Deixe a areia cair livremente no cilindro.")
st.sidebar.write("3. Nivele a superfície com a régua.")
st.sidebar.write("4. Use o valor da densidade gerado aqui no seu App de Ensaio de Campo.")
