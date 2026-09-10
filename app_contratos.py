import streamlit as st
import openpyxl
from io import BytesIO

st.set_page_config(page_title="Gerador Financeiro UFSM", page_icon="💰", layout="wide")

# ==========================================
# DADOS FIXOS DAS TABELAS DO EXCEL
# ==========================================
LISTA_DIARIAS = ["Diárias no país", "Diárias no exterior", "Auxílio para desenvolvimento de estudos e pesquisas", "Diárias a colaboradores eventuais no país"]
LISTA_PF = ["Direitos autorais", "Serviços técnicos profissionais", "Serviços de limpeza e conservação", "Serviços de apoio administrativo, técnico e operacional", "Obrigações Tributárias e Contributivas (cota patronal 20%)"]
LISTA_PASSAGENS = ["Passagens para o país", "Passagens para o exterior", "Locação de meios de transportes", "Locomoção urbana", "Outras despesas com locomoção"]
LISTA_OBRAS = ["Estudos e Projetos", "Obras em andamento", "Instalações", "Almoxarifado de obras", "Outras obras e instalações"]
LISTA_PJ = [
    "Assinaturas de periódicos e anuidades", "Direitos autorais", "Serviços técnicos profissionais", "Manutenção de software", "Locação de imóveis", "Locação de softwares", "Locação de máquinas e equipamentos", "Locação de bens Mov. Out. naturezas e intangíveis", "Manutenção e conservação de bens imóveis", "Manutenção e conservação de máquinas e equipamentos", "Serviço de estacionamento de veículos", "Manutenção e conservação de veículos", "Exposições, congressos e conferências", "Confecção de uniformes", "Desenvolvimento de software", "Suporte de infraestrutura de TI", "Suporte a usuários de TI", "Hospedagem de sistemas", "Locação de equipamentos de processamento de dados", "Fornecimento de alimentação", "Serviços de energia elétrica", "Serviços de água e esgoto", "Serviços de comunicação em geral", "Serviços médico-hospitalar, odontológicos e laboratoriais", "Serviços de análises e pesquisas científicas", "Serviços de tecnologia da informação", "Serviços de telecomunicações", "Serviços de áudio, vídeo e foto", "Serviços de produção industrial", "Serviços gráficos e editoriais", "Seguros em geral", "Confecção de material de acondicionamento e embalagem", "Vale-transporte", "Fretes e transportes de encomendas", "Serviço de apoio administrativo, técnico e operacional", "Hospagens", "Serviços de cópias e reprodução de documentos", "Serviços de publicidade legal", "Aquisição de softwares sob encomenda", "Manutenção e conservação de equip. de processamento de dados", "Comunicação de dados", "Testes e confecções de placas relacionadas ao objeto do projeto", "Outros serviços de terceiros pessoa jurídica"
]
LISTA_CONSUMO = [
    "Combustíveis e lubrificantes automotivos", "Gás e outros materiais engarrafados", "Alimentos para animais", "Gêneros de alimentação", "Animais para pesquisa e abate", "Material farmacológico", "Material odontológico", "Material químico", "Material educativo e esportivo", "Material de expediente", "Material de processamento de dados", "Materiais e medicamentos para uso veterinário", "Material de acondicionamento e embalagem", "Material de copa e cozinha", "Material de limpeza e produtos de higienização", "Uniformes, tecidos e aviamentos", "Material para manutenção de bens imóveis/instalações", "Material para manutenção de bens móveis", "Material elétrico e eletrônico", "Material de proteção e segurança", "Material para áudio, vídeo e foto", "Material para comunicações", "Sementes, mudas de plantas e insumos", "Material para produção industrial", "Material laboratorial", "Material hospitalar", "Material para manutenção de veículos", "Material biológico", "Material para utilização em gráfica", "Ferramentas", "Material de sinalização visual e outros", "Material bibliográfico", "Aquisição de software - produto", "Material para divulgação", "Materiais de Consumo para utilização no laboratório", "Outros Materiais de Consumo"
]

# Inicialização de memória
if 'eq_vinc' not in st.session_state: st.session_state.eq_vinc = []
if 'eq_nao_vinc' not in st.session_state: st.session_state.eq_nao_vinc = []
if 'equip' not in st.session_state: st.session_state.equip = []

col_config_dinheiro = {
    "Valor Parcela": st.column_config.NumberColumn(format="R$ %.2f"),
    "Total": st.column_config.NumberColumn(format="R$ %.2f"),
    "Valor Unitário": st.column_config.NumberColumn(format="R$ %.2f")
}

# Variáveis para a matemática
total_base_infra = 0.0 
total_obras_equip = 0.0

# ==========================================
# BARRA LATERAL FIXA E SELETOR DE FUNDAÇÃO
# ==========================================
# Como o Streamlit lê de cima para baixo, pegamos a escolha da fundação logo no início
fundacao_escolhida = st.sidebar.selectbox(
    "🏛️ Selecione a Fundação",
    ["FATEC", "FAURGS", "FUNDEP", "FDMS"],
    help="As taxas e cálculos são ajustados de acordo com as regras de cada fundação."
)

st.sidebar.divider()

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
st.title("💰 Gerador de Dados Financeiros (Plano de Trabalho)")
st.write("Preencha as informações financeiras abaixo. Acompanhe os cálculos na barra lateral.")

# 1. EQUIPES
st.header("1. Equipe Executora")
with st.expander("Equipe Vinculada à UFSM", expanded=True):
    with st.form("form_vinc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        tipo_remun = c1.text_input("Pessoal Envolvido (Tipo de Remuneração)")
        nome_vinc = c2.text_input("Nome do Membro")
        c3, c4 = st.columns(2)
        siape_mat = c3.text_input("SIAPE / Matrícula")
        cpf_vinc = c4.text_input("CPF")
        c5, c6, c7 = st.columns(3)
        ch_vinc = c5.number_input("Carga Horária (Semanal)", min_value=0, step=1)
        qtd_vinc = c6.number_input("Nº de Pagamentos", min_value=1, step=1)
        valor_vinc = c7.number_input("Valor de cada Pagto (R$)", min_value=0.0, step=100.0)
        
        if st.form_submit_button("Adicionar à Equipe Vinculada") and nome_vinc:
            st.session_state.eq_vinc.append({
                "Tipo Remuneração": tipo_remun, "Nome": nome_vinc, "SIAPE/MAT": siape_mat, 
                "CPF": cpf_vinc, "Carga Horária": ch_vinc, "Nº Pagamentos": qtd_vinc,
                "Valor Parcela": valor_vinc, "Total": valor_vinc * qtd_vinc
            })
            st.rerun()
    if st.session_state.eq_vinc: 
        st.dataframe(st.session_state.eq_vinc, column_config=col_config_dinheiro, hide_index=True, use_container_width=True)

with st.expander("Equipe Não Vinculada"):
    with st.form("form_nao_vinc", clear_on_submit=True):
        c1, c2 = st.columns(2)
        tipo_remun_nv = c1.text_input("Pessoal Envolvido (Tipo de Remuneração)")
        nome_nvinc = c2.text_input("Nome")
        c3, c4 = st.columns(2)
        forma_contrato = c3.text_input("Forma de Contratação (Ex: CLT, RPA)")
        cpf_nvinc = c4.text_input("CPF")
        c5, c6, c7 = st.columns(3)
        ch_nvinc = c5.number_input("Carga Horária (Semanal)", min_value=0, step=1)
        qtd_nvinc = c6.number_input("Nº de Pagamentos", min_value=1, step=1)
        valor_nvinc = c7.number_input("Valor de cada Pagto (R$)", min_value=0.0, step=100.0)
        
        if st.form_submit_button("Adicionar à Equipe Não Vinculada") and nome_nvinc:
            st.session_state.eq_nao_vinc.append({
                "Tipo Remuneração": tipo_remun_nv, "Nome": nome_nvinc, "Forma Contratação": forma_contrato, 
                "CPF": cpf_nvinc, "Carga Horária": ch_nvinc, "Nº Pagamentos": qtd_nvinc,
                "Valor Parcela": valor_nvinc, "Total": valor_nvinc * qtd_nvinc
            })
            st.rerun()
    if st.session_state.eq_nao_vinc: 
        st.dataframe(st.session_state.eq_nao_vinc, column_config=col_config_dinheiro, hide_index=True, use_container_width=True)

total_base_infra += sum(item["Total"] for item in st.session_state.eq_vinc)
total_base_infra += sum(item["Total"] for item in st.session_state.eq_nao_vinc)

# 2. TABELAS FIXAS
st.header("2. Despesas e Serviços")
def renderizar_tabela_fixa(titulo, lista_itens, prefixo_chave):
    valores = {}
    with st.expander(titulo):
        for item in lista_itens:
            val = st.number_input(item, min_value=0.0, step=50.0, key=f"{prefixo_chave}_{item}")
            if val > 0: valores[item] = val
    return valores

dados_diarias = renderizar_tabela_fixa("4.2 - Diárias", LISTA_DIARIAS, "diaria")
dados_pj = renderizar_tabela_fixa("4.3 - Serviços de Terceiros (PJ)", LISTA_PJ, "pj")
dados_pf = renderizar_tabela_fixa("4.4 - Serviços de Terceiros (PF)", LISTA_PF, "pf")
dados_passagens = renderizar_tabela_fixa("4.5 - Passagens e Locomoção", LISTA_PASSAGENS, "pass")
dados_consumo = renderizar_tabela_fixa("4.6 - Material de Consumo", LISTA_CONSUMO, "cons")
dados_obras = renderizar_tabela_fixa("4.8 - Obras e Instalações (Isento de Taxa UFSM)", LISTA_OBRAS, "obras")

# Soma na base tributável da UFSM
for d in [dados_diarias, dados_pj, dados_pf, dados_passagens, dados_consumo]:
    total_base_infra += sum(d.values())

# Obras não pagam infra UFSM
total_obras_equip += sum(dados_obras.values())

# 3. ANEXO I (Equipamentos) - Isentos de Taxa UFSM
st.header("3. Anexo I - Material Permanente")
with st.expander("Equipamento Permanente (Isento de Taxa UFSM)", expanded=True):
    with st.form("form_equip", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        desc_eq = c1.text_input("Especificação")
        qtd_eq = c2.number_input("Quantidade", min_value=1, step=1)
        val_eq = c3.number_input("Valor Unitário (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Adicionar Equipamento") and desc_eq:
            st.session_state.equip.append({"Especificação": desc_eq, "Quantidade": qtd_eq, "Valor Unitário": val_eq, "Total": qtd_eq * val_eq})
            st.rerun()
    if st.session_state.equip: 
        st.dataframe(st.session_state.equip, column_config=col_config_dinheiro, hide_index=True, use_container_width=True)
    
total_obras_equip += sum(item["Total"] for item in st.session_state.equip)

# ==========================================
# CÁLCULOS MATEMÁTICOS FINAIS
# ==========================================
subtotal_projeto = total_base_infra + total_obras_equip

# Taxa Infra UFSM
taxa_ufsm = 0.08 if total_base_infra > 200000 else 0.05
valor_infra_ufsm = total_base_infra * taxa_ufsm

# Taxa Operacional Fundação
if fundacao_escolhida in ["FATEC", "FDMS"]:
    valor_taxa_fundacao = subtotal_projeto * 0.10
else:
    # Gross-up FAURGS/FUNDEP
    valor_taxa_fundacao = ((subtotal_projeto + valor_infra_ufsm) / 0.9) * 0.10

total_geral_final = subtotal_projeto + valor_infra_ufsm + valor_taxa_fundacao

# ==========================================
# RENDERIZAÇÃO DA BARRA LATERAL (Cálculos)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/UFSM_bras%C3%A3o_e_logotipo.png/320px-UFSM_bras%C3%A3o_e_logotipo.png", width=150)
    st.title("Detalhamento Financeiro")
    
    st.caption("Custos Diretos (Equipe + Despesas)")
    st.write(f"R$ {subtotal_projeto:,.2f}")
    
    st.caption(f"Infraestrutura UFSM ({int(taxa_ufsm*100)}%)")
    st.write(f"R$ {valor_infra_ufsm:,.2f}")
    
    tipo_calculo = "Direto" if fundacao_escolhida in ["FATEC", "FDMS"] else "Gross-up"
    st.caption(f"Taxa da Fundação ({tipo_calculo})")
    st.write(f"R$ {valor_taxa_fundacao:,.2f}")
    
    st.divider()
    st.metric("TOTAL GERAL DO PROJETO", f"R$ {total_geral_final:,.2f}")
    st.divider()
    
    if st.button("📥 GERAR ARQUIVO", type="primary", use_container_width=True):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        def criar_aba_dinamica(titulo, dados):
            ws = wb.create_sheet(titulo)
            if dados:
                ws.append(list(dados[0].keys()))
                for linha in dados: ws.append(list(linha.values()))
            else:
                ws.append(["Nenhum item cadastrado"])

        def criar_aba_fixa(titulo, dicionario):
            ws = wb.create_sheet(titulo)
            ws.append(["Categoria", "Valor (R$)"])
            if dicionario:
                for cat, val in dicionario.items(): ws.append([cat, val])
            else:
                ws.append(["Nenhum item preenchido"])

        # Identificador para o Raichu
        ws_config = wb.create_sheet("Config_Raichu")
        ws_config.append(["Fundacao_Escolhida", fundacao_escolhida])

        criar_aba_dinamica("Equipe_Vinc", st.session_state.eq_vinc)
        criar_aba_dinamica("Equipe_Nao_Vinc", st.session_state.eq_nao_vinc)
        criar_aba_fixa("Diarias", dados_diarias)
        criar_aba_fixa("Servicos_PJ", dados_pj)
        criar_aba_fixa("Servicos_PF", dados_pf)
        criar_aba_fixa("Passagens", dados_passagens)
        criar_aba_fixa("Consumo", dados_consumo)
        criar_aba_fixa("Obras", dados_obras)
        criar_aba_dinamica("Anexo_1", st.session_state.equip)

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        st.success("Arquivo gerado! Envie-o para o preenchimento automático.")
        st.download_button(
            label="📥 Baixar Dados_Financeiros.xlsx",
            data=output,
            file_name="Dados_Financeiros.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
