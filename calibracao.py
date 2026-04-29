import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Ensaios", page_icon="🏗️", layout="centered")

# --- CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'

def mudar_pagina(nome):
    st.session_state.pagina = nome

# ==========================================
# TELA DE ESCOLHA (MENU INICIAL)
# ==========================================
if st.session_state.pagina == 'home':
    st.title("🏗️ Selecione o Ensaio")
    st.write("Qual formulário você vai preencher agora?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 DENSIDADE IN SITU (METROSUL)", use_container_width=True):
            mudar_pagina('metrosul')
            st.rerun()
            
    with col2:
        if st.button("🏗️ ENSAIO DCP (CORSAN)", use_container_width=True):
            mudar_pagina('corsan')
            st.rerun()

# ==========================================
# CÓDIGO 1: METROSUL (DENSIDADE)
# ==========================================
elif st.session_state.pagina == 'metrosul':
    if st.button("⬅️ Voltar ao Menu"):
        mudar_pagina('home')
        st.rerun()

    def gerar_pdf_ensaio(d):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "RELATORIO DE ENSAIO - FRASCO DE AREIA", ln=True, align='C')
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, "Padrao Operacional - Ambiental Metrosul", ln=True, align='C')
        pdf.ln(5)
        
        def criar_tabela(titulo, linhas):
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(190, 7, f" {titulo}", border=1, ln=True, fill=True)
            pdf.set_font("Arial", "", 10)
            for desc, valor in linhas:
                pdf.cell(140, 8, f" {desc}", border=1)
                pdf.cell(50, 8, f" {valor}", border=1, ln=True, align='R')
            pdf.ln(3)
        
        criar_tabela("1. DETERMINACAO DA UMIDADE", [
            ("A - Tara do recipiente (g)", f"{d['u_a']:.3f}"),
            ("B - Peso do solo umido + recipiente (g)", f"{d['u_b']:.3f}"),
            ("C - Peso do solo seco + recipiente (g)", f"{d['u_c']:.3f}"),
            ("D - Peso solo umido (B - A) (g)", f"{d['u_d']:.3f}"),
            ("E - Peso solo seco (C - A) (g)", f"{d['u_e']:.3f}"),
            ("F - Peso agua (D - E) (g)", f"{d['u_f']:.3f}"),
            ("G - Teor de umidade - w (%)", f"{d['u_g']:.2f} %")
        ])
        criar_tabela("2. DETERMINACAO DA DENSIDADE IN SITU", [
            ("A - Massa inicial (aparelho + areia) (g)", f"{d['d_a']:.3f}"),
            ("B - Massa final (aparelho + areia) (g)", f"{d['d_b']:.3f}"),
            ("C - Peso da areia consumida (A - B) (g)", f"{d['d_c']:.3f}"),
            ("D - Massa areia no cone (g)", f"{d['d_d']:.3f}"),
            ("E - Massa areia no buraco (C - D) (g)", f"{d['d_e']:.3f}"),
            ("F - Densidade da areia (g/cm3)", f"{d['d_f']:.3f}"),
            ("G - Volume do buraco (E / F) (cm3)", f"{d['d_g']:.4f}"),
            ("H - Massa solo umido + bandeja (g)", f"{d['d_h_total']:.3f}"),
            ("I - Tara da bandeja da cava (g)", f"{d['d_h_tara']:.3f}"),
            ("J - Massa especifica seca (g/cm3)", f"{d['d_j']:.3f}")
        ])
        
        pdf.set_font("Arial", "B", 12)
        cor = (0, 100, 0) if d['gc'] >= 95 else (200, 0, 0)
        pdf.set_text_color(*cor)
        pdf.cell(190, 12, f"GRAU DE COMPACTACAO FINAL: {d['gc']:.1f} %", border=1, ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', 'ignore')

    st.title("🧪 Painel de Controle - Metrosul")
    
    with st.expander("💧 1. Determinação da Umidade", expanded=True):
        col1, col2 = st.columns(2)
        u_a = col1.number_input("A - Tara da Bandeja Pequena (g)", format="%.3f", step=0.001, key="t_u")
        u_b = col2.number_input("B - Solo Úmido + Bandeja (g)", format="%.3f", step=0.001, key="s_u")
        u_c = st.number_input("C - Solo Seco + Bandeja (g)", format="%.3f", step=0.001, key="s_s")
        
        u_d = u_b - u_a
        u_e = u_c - u_a
        u_f = u_d - u_e
        u_g = (u_f / u_e) * 100 if u_e > 0 else 0.0
        
        st.write("---")
        res1, res2, res3 = st.columns(3)
        res1.metric("Solo Úmido (D)", f"{u_d:.3f}")
        res2.metric("Solo Seco (E)", f"{u_e:.3f}")
        res3.metric("Peso Água (F)", f"{u_f:.3f}")
        st.info(f"**Teor de Umidade (w): {u_g:.2f}%**")

    with st.expander("⚖️ 2. Densidade In Situ", expanded=True):
        col_d1, col_d2 = st.columns(2)
        d_a = col_d1.number_input("A - Massa Inicial (Frasco+Areia) (g)", format="%.3f", step=0.001)
        d_b = col_d2.number_input("B - Massa Final (Frasco+Areia) (g)", format="%.3f", step=0.001)
        
        col_d3, col_d4 = st.columns(2)
        d_d = col_d3.number_input("D - Massa Areia no Cone (g)", format="%.3f", step=0.001, value=0.533)
        d_f = col_d4.number_input("F - Densidade da Areia (g/cm³)", format="%.3f", step=0.001, value=1.422)
        
        d_h_total = st.number_input("H - Massa Solo Úmido + Bandeja da Cava (g)", format="%.3f", step=0.001)
        d_h_tara = st.number_input("Tara da Bandeja da Cava (g)", format="%.3f", step=0.001, value=0.240, key="t_c")
        
        d_h_liquido = d_h_total - d_h_tara
        d_c = d_a - d_b
        d_e = d_c - d_d
        d_g = d_e / d_f if d_f > 0 else 0.0
        d_i = d_h_liquido / d_g if d_g > 0 else 0.0
        d_j = d_i / (1 + (u_g / 100)) if u_e > 0 else 0.0
        
        st.write("---")
        rd1, rd2, rd3 = st.columns(3)
        rd1.metric("Areia Buraco (E)", f"{d_e:.3f}")
        rd2.metric("Volume (G)", f"{d_g:.4f}")
        rd3.metric("Solo Líquido", f"{d_h_liquido:.3f}")
        st.success(f"**Massa Seca de Campo (J): {d_j:.3f} g/cm³**")

    st.divider()
    proctor = st.number_input("Proctor Máximo Lab (g/cm³)", format="%.3f", step=0.001, value=1.785)
    gc = (d_j / proctor) * 100 if proctor > 0 else 0.0
    st.metric("GRAU DE COMPACTAÇÃO", f"{gc:.1f}%")
    
    if gc > 0:
        dados_pdf = {
            'u_a':u_a, 'u_b':u_b, 'u_c':u_c, 'u_d':u_d, 'u_e':u_e, 'u_f':u_f, 'u_g':u_g,
            'd_a':d_a, 'd_b':d_b, 'd_c':d_c, 'd_d':d_d, 'd_e':d_e, 'd_f':d_f, 'd_g':d_g, 
            'd_h_total':d_h_total, 'd_h_tara':d_h_tara, 'd_i':d_i, 'd_j':d_j, 'gc':gc
        }
        st.download_button("📥 Baixar Relatório PDF", gerar_pdf_ensaio(dados_pdf), "Relatorio_Metrosul.pdf", "application/pdf", use_container_width=True)

# ==========================================
# CÓDIGO 2: CORSAN (DCP)
# ==========================================
elif st.session_state.pagina == 'corsan':
    if st.button("⬅️ Voltar ao Menu"):
        mudar_pagina('home')
        st.rerun()

    def parse_float(valor_str: str) -> float:
        if not valor_str: return 0.0
        v_limpo = valor_str.strip().replace(',', '.')
        try: return float(v_limpo)
        except ValueError: return 0.0

    def gerar_pdf_dcp(dados):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 18); pdf.set_text_color(15, 76, 129)
        pdf.cell(190, 12, "RELATÓRIO DE ENSAIO DCP", ln=True, align='C')
        pdf.set_font("Arial", "", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 6, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(8)
        pdf.set_font("Arial", "B", 12); pdf.set_fill_color(240, 248, 255)
        pdf.cell(190, 8, "DADOS DA OBRA", border=1, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 8, f"OS: {dados['os']}", border=1)
        pdf.cell(95, 8, f"Material: {dados['material']}", border=1, ln=True)
        pdf.multi_cell(190, 8, f"Local: {dados['endereco']}", border=1)
        pdf.ln(4)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(45, 10, "Golpes", border=1); pdf.cell(55, 10, "Penetração (mm)", border=1); pdf.cell(90, 10, "IPD Parcial", border=1, ln=True)
        pdf.set_font("Arial", "", 10)
        for i, leitura in enumerate(dados['leituras'], start=1):
            golpes = i * 3
            ipd_p = (leitura - dados['marco_zero']) / golpes
            pdf.cell(45, 8, str(golpes), border=1); pdf.cell(55, 8, f"{leitura:.1f}", border=1); pdf.cell(90, 8, f"{ipd_p:.2f}", border=1, ln=True)
        pdf.ln(8)
        pdf.set_font("Arial", "B", 13)
        pdf.cell(190, 10, f"STATUS: {dados['status']}", border=1, ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', errors='ignore')

    if 'leituras' not in st.session_state: st.session_state.leituras = []
    if 'material' not in st.session_state: st.session_state.material = "BGS"
    if 'limites' not in st.session_state: st.session_state.limites = {"BGS": 6.0, "Solo": 17.0, "Areia": 22.0}

    st.title("🏗️ Ensaio DCP - Corsan")
    os_id = st.text_input("Número da OS / Contrato")
    endereco = st.text_input("Local / Endereço")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    if col_m1.button("🟤 BGS"): st.session_state.material = "BGS"
    if col_m2.button("🟠 Solo"): st.session_state.material = "Solo"
    if col_m3.button("🟡 Areia"): st.session_state.material = "Areia"
    
    limite = st.session_state.limites[st.session_state.material]
    st.info(f"Material: {st.session_state.material} | Limite: {limite:.2f}")
    
    marco_zero = parse_float(st.text_input("Marco Zero (mm)", value="0.0"))
    
    for idx, leitura in enumerate(st.session_state.leituras):
        col_v, col_d = st.columns([5, 1])
        st.session_state.leituras[idx] = parse_float(col_v.text_input(f"Leitura {(idx+1)*3} golpes", value=f"{leitura:.1f}", key=f"dcp_{idx}"))
        if col_d.button("🗑️", key=f"del_{idx}"):
            st.session_state.leituras.pop(idx); st.rerun()
            
    if st.button("➕ Adicionar leitura"):
        st.session_state.leituras.append(0.0); st.rerun()
        
    if st.session_state.leituras:
        ipdf = (st.session_state.leituras[-1] - marco_zero) / (len(st.session_state.leituras) * 3)
        st.metric("IPD Final", f"{ipdf:.2f}")
        if os_id and endereco:
            status = "APROVADO" if ipdf <= limite else "RECOMPACTAR"
            d_pdf = {"os": os_id, "endereco": endereco, "material": st.session_state.material, "marco_zero": marco_zero, "leituras": st.session_state.leituras, "ipd_final": ipdf, "status": status}
            st.download_button("📄 Baixar PDF DCP", gerar_pdf_dcp(d_pdf), f"DCP_{os_id}.pdf", "application/pdf", use_container_width=True)
