import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io
import re

# ==================== CONFIGURAÇÃO GLOBAL ====================
st.set_page_config(page_title="Sistema de Ensaios", page_icon="🏗️", layout="centered")

# Controle de Navegação
if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'

def mudar_pagina(nome):
    st.session_state.pagina = nome

# ==========================================
# MENU INICIAL
# ==========================================
if st.session_state.pagina == 'home':
    st.title("🏗️ Selecione o Ensaio")
    st.write("Escolha qual formulário deseja preencher:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 DENSIDADE IN SITU (METROSUL)", use_container_width=True):
            mudar_pagina('metrosul')
            st.rerun()
            
    with col2:
        if st.button("🏗️ ENSAIO DCP (METROSUL)", use_container_width=True):
            mudar_pagina('corsan')
            st.rerun()

# ==========================================
# CÓDIGO 1: METROSUL
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
        dados_pdf = {'u_a':u_a, 'u_b':u_b, 'u_c':u_c, 'u_d':u_d, 'u_e':u_e, 'u_f':u_f, 'u_g':u_g,
                     'd_a':d_a, 'd_b':d_b, 'd_c':d_c, 'd_d':d_d, 'd_e':d_e, 'd_f':d_f, 'd_g':d_g, 
                     'd_h_total':d_h_total, 'd_h_tara':d_h_tara, 'd_i':d_i, 'd_j':d_j, 'gc':gc}
        st.download_button("📥 Baixar Relatório PDF", gerar_pdf_ensaio(dados_pdf), "Relatorio_Metrosul.pdf", "application/pdf", use_container_width=True)

# ==========================================
# CÓDIGO 2: CORSAN (DCP)
# ==========================================
elif st.session_state.pagina == 'corsan':
    if st.button("⬅️ Voltar ao Menu"):
        mudar_pagina('home')
        st.rerun()

    st.markdown("""
    <style>
        .main-title { font-size: 2.2rem; font-weight: 700; color: #0F4C81; text-align: center; margin-bottom: 0.5rem; }
        .sub-title { font-size: 1rem; text-align: center; color: #4B5563; margin-bottom: 2rem; }
        .section-header { font-size: 1.3rem; font-weight: 600; color: #1F2937; border-left: 5px solid #0F4C81; padding-left: 0.8rem; margin: 1.5rem 0 1rem 0; }
        .metric-card { background-color: #F8FAFC; border-radius: 0.75rem; padding: 0.8rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .status-approved { background-color: #DCFCE7; border-left: 6px solid #22C55E; padding: 0.8rem; border-radius: 0.5rem; font-weight: 600; }
        .status-reject { background-color: #FEE2E2; border-left: 6px solid #EF4444; padding: 0.8rem; border-radius: 0.5rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    def parse_float(valor_str: str) -> float:
        if not valor_str: return 0.0
        v_limpo = valor_str.strip().replace(',', '.')
        try: return float(v_limpo)
        except ValueError: return 0.0

    def calcular_ipd(marco_zero: float, leituras: list) -> dict:
        if not leituras: return {"ipd": 0.0, "golpes": 0, "status": "SEM DADOS"}
        ultima = leituras[-1]
        golpes_total = len(leituras) * 3
        ipd = (ultima - marco_zero) / golpes_total if golpes_total > 0 else 0.0
        return {"ipd": ipd, "golpes": golpes_total, "ultima_leitura": ultima}

    def gerar_pdf(dados: dict) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 18); pdf.set_text_color(15, 76, 129)
        pdf.cell(190, 12, "RELATÓRIO DE ENSAIO DCP", ln=True, align='C')
        pdf.set_font("Arial", "", 10); pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 6, f"Data do ensaio: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", ln=True, align='C'); pdf.ln(8)
        pdf.set_font("Arial", "B", 12); pdf.set_fill_color(240, 248, 255)
        pdf.cell(190, 8, "DADOS DA OBRA", border=1, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 8, f"OS / Contrato: {dados['os']}", border=1)
        pdf.cell(95, 8, f"Material: {dados['material']}", border=1, ln=True)
        pdf.multi_cell(190, 8, f"Local / Endereço: {dados['endereco']}", border=1); pdf.ln(4)
        pdf.set_font("Arial", "B", 12); pdf.cell(190, 8, "PARÂMETROS DE REFERÊNCIA", border=1, ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 8, f"Limite aceitável (IPD máx): {dados['limite_ref']:.2f} mm/golpe", border=1)
        pdf.cell(95, 8, f"Penetração inicial (marco zero): {dados['marco_zero']:.1f} mm", border=1, ln=True); pdf.ln(4)
        pdf.set_font("Arial", "B", 11); pdf.cell(45, 10, "Golpes", border=1, align='C'); pdf.cell(55, 10, "Penetração (mm)", border=1, align='C'); pdf.cell(90, 10, "IPD Parcial (mm/golpe)", border=1, align='C', ln=True)
        pdf.set_font("Arial", "", 10); pdf.cell(45, 8, "0", border=1, align='C'); pdf.cell(55, 8, f"{dados['marco_zero']:.1f}", border=1, align='C'); pdf.cell(90, 8, "-", border=1, align='C', ln=True)
        for i, leitura in enumerate(dados['leituras'], start=1):
            golpes = i * 3
            ipd_parcial = (leitura - dados['marco_zero']) / golpes
            pdf.cell(45, 8, str(golpes), border=1, align='C'); pdf.cell(55, 8, f"{leitura:.1f}", border=1, align='C'); pdf.cell(90, 8, f"{ipd_parcial:.2f}", border=1, align='C', ln=True)
        pdf.ln(8); pdf.set_font("Arial", "B", 13)
        cor = (34, 197, 94) if dados['status'] == "APROVADO" else (239, 68, 68)
        pdf.set_text_color(*cor); pdf.cell(190, 10, f"STATUS: {dados['status']}", border=1, ln=True, align='C')
        pdf.set_font("Arial", "B", 11); pdf.set_text_color(0, 0, 0); pdf.cell(190, 9, f"IPD FINAL: {dados['ipd_final']:.2f} mm/golpe", border=1, ln=True, align='C')
        pdf.set_y(-20); pdf.set_font("Arial", "I", 8); pdf.cell(190, 5, "Relatório gerado pelo sistema Corsan - Ensaio DCP", ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', errors='ignore')

    if 'leituras' not in st.session_state: st.session_state.leituras = []
    if 'material' not in st.session_state: st.session_state.material = "BGS"
    if 'limites' not in st.session_state: st.session_state.limites = {"BGS": 6.0, "Solo": 17.0, "Areia": 22.0}

    with st.sidebar:
        st.markdown("## ⚙️ Configurações")
        novo_bgs = st.number_input("🟤 BGS (mm/golpe)", value=st.session_state.limites["BGS"], step=0.1)
        novo_solo = st.number_input("🟠 Solo (mm/golpe)", value=st.session_state.limites["Solo"], step=0.1)
        novo_areia = st.number_input("🟡 Areia (mm/golpe)", value=st.session_state.limites["Areia"], step=0.1)
        if st.button("💾 Salvar"):
            st.session_state.limites.update({"BGS": novo_bgs, "Solo": novo_solo, "Areia": novo_areia})
            st.success("Salvo!")

    st.markdown('<div class="main-title">🏗️ Ensaio de Compactação DCP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Corsan - Controle de qualidade</div>', unsafe_allow_html=True)
    
    col_os, col_local = st.columns(2)
    os_id = col_os.text_input("Número da OS / Contrato")
    endereco = col_local.text_input("Local / Endereço")

    col_mat1, col_mat2, col_mat3 = st.columns(3)
    if col_mat1.button("🟤 BGS", use_container_width=True): st.session_state.material = "BGS"
    if col_mat2.button("🟠 Solo", use_container_width=True): st.session_state.material = "Solo"
    if col_mat3.button("🟡 Areia", use_container_width=True): st.session_state.material = "Areia"

    limite_atual = st.session_state.limites[st.session_state.material]
    st.info(f"📌 Material: **{st.session_state.material}** | Limite: **≤ {limite_atual:.2f}**")

    marco_zero = parse_float(st.text_input("Penetração inicial (mm)", value="0.0"))

    for idx, leitura in enumerate(st.session_state.leituras):
        col_val, col_del = st.columns([5, 1])
        st.session_state.leituras[idx] = parse_float(col_val.text_input(f"Leitura {(idx+1)*3} golpes (mm)", value=f"{leitura:.1f}", key=f"leitura_{idx}"))
        if col_del.button("🗑️", key=f"del_{idx}"):
            st.session_state.leituras.pop(idx)
            st.rerun()

    if st.button("➕ Adicionar leitura (3 golpes)", use_container_width=True):
        st.session_state.leituras.append(0.0)
        st.rerun()

    if st.session_state.leituras:
        calc = calcular_ipd(marco_zero, st.session_state.leituras)
        status = "APROVADO" if calc["ipd"] <= limite_atual else "RECOMPACTAR"
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("IPD Final", f"{calc['ipd']:.2f}")
        c2.metric("Golpes", f"{calc['golpes']}")
        c3.metric("Final (mm)", f"{calc['ultima_leitura']:.1f}")
        
        if status == "APROVADO":
            st.markdown(f'<div class="status-approved">✅ STATUS: {status}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-reject">⚠️ STATUS: {status}</div>', unsafe_allow_html=True)

        if os_id and endereco:
            d_pdf = {"os": os_id, "endereco": endereco, "material": st.session_state.material, "marco_zero": marco_zero, "leituras": st.session_state.leituras, "ipd_final": calc["ipd"], "status": status, "limite_ref": limite_atual}
            st.download_button("📄 Baixar PDF", gerar_pdf(d_pdf), f"DCP_{os_id}.pdf", "application/pdf", use_container_width=True)
