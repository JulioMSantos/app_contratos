import streamlit as st
import pandas as pd
import graphviz
import textwrap

st.set_page_config(layout="wide", page_title="Sistema Integra", page_icon="📊")

if 'nap_autenticado' not in st.session_state:
    st.session_state['nap_autenticado'] = False

# ==========================================
# 1. CSS MODERNIZADO
# ==========================================
st.markdown("""
    <style>
        [data-testid="stGraphVizChart"] {
            overflow: auto; 
            background-color: #F8F9FA; 
            border-radius: 15px; 
            padding: 20px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: center;
        }
        [data-testid="stGraphVizChart"] > svg {
            max-width: 100% !important; 
            height: auto !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO COM O GOOGLE PLANILHAS
# ==========================================
url_google_sheets = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRXE69ipW9usXVW5msH5SPVV5CMz5tboAlWg_O-9Zdi4_WGxdB5BmTlXxdd_2OSrW6_S91J66bckSDs/pub?gid=409266791&single=true&output=csv"

try:
    df_bruto = pd.read_csv(url_google_sheets, dtype=str)
    df_bruto.columns = df_bruto.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
    
    df = df_bruto.rename(columns={
        'Registro Portal de Projetos': 'Registro',
        'Projeto/Título': 'Titulo',
        'Etapa Atual': 'Etapa_Atual',
        'Coordenador': 'Coordenador' 
    })
    
    colunas_essenciais = ['Registro', 'Titulo', 'Etapa_Atual', 'Coordenador']
    for col in colunas_essenciais:
        if col not in df.columns: df[col] = "" 
            
    df['Registro'] = df['Registro'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['Titulo'] = df['Titulo'].astype(str).str.strip()
    df['Etapa_Atual'] = df['Etapa_Atual'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['Coordenador'] = df['Coordenador'].astype(str).str.strip()

except Exception as e:
    df = pd.DataFrame(columns=['Registro', 'Titulo', 'Etapa_Atual', 'Coordenador'])


# ==========================================
# 3. MOTOR MULTI-CONTRATOS (DADOS AP e Licenciamento)
# ==========================================
def carregar_modelo_contrato(tipo_contrato):
    
    if tipo_contrato == "Acordo de Parceria":
        tradutor = {
            '1': 'N_C1', '2': 'N_C2', '3': 'N_C3', '4': 'N_V4', '5': 'N_V5', '6': 'N_C6', '7': 'N_V7', '8': 'N_A8', '9': 'N_A9', '10': 'N_V10',
            '11': 'N_V11', '12': 'N_V12', '13': 'N_C13', '14.1': 'N_V14_1', '14.2': 'N_V14_2', '15.1': 'N_A15_1', '15.2.1': 'N_J15_2_1',
            '15.2.2': 'N_J15_2_2', '15.3': 'N_C15_3', '16.2.1': 'N_PI16_2_1', '16.2.2': 'N_V16_2_2', '16.2.3': 'N_V16_2_3', '17.2.1': 'N_C17_2_1',
            '17.2.2': 'N_V17_2_2', '17.3': 'N_A17_3', '18.1': 'N_O18_1', '18.2.1': 'N_PI18_2_1', '18.2.2': 'N_V18_2_2', '19.1': 'N_O19_1',
            '19.2.1': 'N_PI19_2_1', '19.2.2': 'N_V19_2_2', '20.1': 'N_A20_1', '20.2.1': 'N_J20_2_1', '20.2.2': 'N_V20_2_2', '20.3': 'N_A20_3',
            '21.2': 'N_J21_2', '22.1': 'N_A22_1', '23.1': 'N_A23_1', '24': 'N_O24', '25': 'N_O25', '26': 'N_O26', '27': 'N_O27'
        }
        textos = {
            'N_INICIO': 'Início', 'N_C1': '1. Abrir processo no PEN', 'N_C_D1': 'Algum documento acordado?', 'N_C2': '2. Anexar ao PEN',
            'N_C3': '3. Tramitar para NPV', 'N_C6': '6. Elaborar proposta', 'N_C13': '13. Responder e-mail', 'N_C15_3': '15.3 Enviar doc',
            'N_C17_2_1': '17.2.1 Enviar ao NPI', 'N_V4': '4. Reunião de projeto', 'N_V5': '5. Enviar material', 'N_V_D1': 'Divisão de PI?',
            'N_V_D2': 'Precisa valorar?', 'N_V10_2_2': '10.2.2 Valoração', 'N_V_SEGUIR': 'Seguir independentemente', 'N_V_D3': 'Negociação NPV?',
            'N_V10': '10. Negociar proposta', 'N_V11': '11. Tramitar ao NAP', 'N_V7': '7. Tramitar ao NAP', 'N_V12': '12. Modelo Escolha Fundação',
            'N_V14_1': '14.1 Doc instrução processual', 'N_V14_2': '14.2 Encaminhar ao jurídico', 'N_V_D4': 'Tipo de negociação de TT?',
            'N_V16_2_3': '16.2.3 Negociar cláusulas', 'N_V20_2_2': '20.2.2 Relatório negociação', 'N_V16_2_2': '16.2.2 Valoração',
            'N_V17_2_2': '17.2.2 Parecer técnico valoração', 'N_V18_2_2': '18.2.2 Parecer de valoração', 'N_V19_2_2': '19.2.2 Enviar Jurídico',
            'N_A8': '8. Analisar Enquadramento', 'N_A_D1': 'É Acordo de parceria?', 'N_A_SEGUIR': 'Seguir enquadramento', 'N_FIM': 'FIM',
            'N_A9': '9. Tramitar ao NPV', 'N_A15_1': '15.1 Analisar documentação', 'N_A17_3': '17.3 Enviar PRA', 'N_A_D2': 'Doc precisa correção?',
            'N_A20_3': '20.3 Retornar ao coordenador', 'N_A20_1': '20.1 Solicitar Fundação', 'N_A22_1': '22.1 Coletar assinaturas',
            'N_A23_1': '23.1 Tramitar para a PRA', 'N_J_D1': 'Empresa tem própria minuta?', 'N_J15_2_1': '15.2.1 Analisar minuta',
            'N_J15_2_2': '15.2.2 Minuta padrão AGU', 'N_J_D2': 'Tem divisão de PI?', 'N_J_D3': 'Negociar TT?', 'N_J20_2_1': '20.2.1 Elaborar minuta',
            'N_J21_2': '21.2 Fechar a minuta', 'N_J_D4': 'Quadro comparativo?', 'N_PI16_2_1': '16.2.1 Declaração atividades',
            'N_PI18_2_1': '18.2.1 Percentual PI', 'N_PI19_2_1': '19.2.1 Enviar partes', 'N_O18_1': '18.1 Analisar doc (PRA)',
            'N_O19_1': '19.1 Enviar NAP (PRA)', 'N_O24': '24. Realizar análise (PRA)', 'N_O25': '25. Emitir parecer (PRA)',
            'N_O26': '26. Inserir CADIN (PRA)', 'N_O27': '27. Tramitar ao NAP (PRA)'
        }
        setores = {
            'Coordenador(a)': ['N_INICIO', 'N_C1', 'N_C_D1', 'N_C2', 'N_C3', 'N_C6', 'N_C13', 'N_C15_3', 'N_C17_2_1'],
            'NPV': ['N_V4', 'N_V5', 'N_V_D1', 'N_V_D2', 'N_V10_2_2', 'N_V_SEGUIR', 'N_V_D3', 'N_V10', 'N_V11', 'N_V7', 'N_V12', 'N_V14_1', 'N_V14_2', 'N_V_D4', 'N_V16_2_3', 'N_V20_2_2', 'N_V16_2_2', 'N_V17_2_2', 'N_V18_2_2', 'N_V19_2_2'],
            'Juridico': ['N_J_D1', 'N_J15_2_1', 'N_J15_2_2', 'N_J_D2', 'N_J_D3', 'N_J20_2_1', 'N_J21_2', 'N_J_D4'],
            'NPI': ['N_PI16_2_1', 'N_PI18_2_1', 'N_PI19_2_1'],
            'NAP': ['N_A8', 'N_A_D1', 'N_A_SEGUIR', 'N_FIM', 'N_A9', 'N_A15_1', 'N_A17_3', 'N_A_D2', 'N_A20_3', 'N_A20_1', 'N_A22_1', 'N_A23_1'],
            'Outros': ['N_O18_1', 'N_O19_1', 'N_O24', 'N_O25', 'N_O26', 'N_O27']
        }
        conexoes = [
            ('N_INICIO', 'N_C1'), ('N_C1', 'N_C_D1'), ('N_C_D1', 'N_C2', 'Sim'), ('N_C_D1', 'N_C3', 'Não'), ('N_C2', 'N_C3'),
            ('N_C3', 'N_V4'), ('N_V4', 'N_V5'), ('N_V5', 'N_V_D1'), ('N_V_D1', 'N_C6', 'Sim'), ('N_C6', 'N_V7'), ('N_V_D1', 'N_V_D2', 'Não'),
            ('N_V_D2', 'N_V10_2_2', 'Sim'), ('N_V_D2', 'N_V_SEGUIR', 'Não'), ('N_V10_2_2', 'N_V_D3'), ('N_V_SEGUIR', 'N_V_D3'),
            ('N_V_D3', 'N_V10', 'Sim'), ('N_V10', 'N_V11'), ('N_V_D3', 'N_V7', 'Não'), ('N_V11', 'N_A8'), ('N_V7', 'N_A8'),
            ('N_A8', 'N_A_D1'), ('N_A_D1', 'N_A_SEGUIR', 'Não'), ('N_A_SEGUIR', 'N_FIM'), ('N_A_D1', 'N_A9', 'Sim'), ('N_A9', 'N_V12'),
            ('N_V12', 'N_C13'), ('N_C13', 'N_V14_1'), ('N_V14_1', 'N_C15_3'), ('N_C15_3', 'N_V14_2'), ('N_V14_2', 'N_J_D1'),
            ('N_V14_2', 'N_A15_1'), ('N_J_D1', 'N_J15_2_1', 'Sim'), ('N_J_D1', 'N_J15_2_2', 'Não'), ('N_J15_2_1', 'N_J_D2'),
            ('N_J15_2_2', 'N_J_D2'), ('N_J_D2', 'N_PI16_2_1', 'Sim'), ('N_PI16_2_1', 'N_C17_2_1'), ('N_C17_2_1', 'N_PI18_2_1'),
            ('N_PI18_2_1', 'N_PI19_2_1'), ('N_PI19_2_1', 'N_J20_2_1'), ('N_J_D2', 'N_J_D3', 'Não'), ('N_J_D3', 'N_J20_2_1', 'Não'),
            ('N_J_D3', 'N_V_D4', 'Sim'), ('N_V_D4', 'N_V16_2_3', 'Diferentes'), ('N_V16_2_3', 'N_V20_2_2'), ('N_V20_2_2', 'N_J20_2_1'),
            ('N_V_D4', 'N_V16_2_2', 'Valoração'), ('N_V16_2_2', 'N_V17_2_2'), ('N_V17_2_2', 'N_V18_2_2'), ('N_V18_2_2', 'N_V19_2_2'),
            ('N_V19_2_2', 'N_J20_2_1'), ('N_J20_2_1', 'N_J21_2'), ('N_J21_2', 'N_J_D4'), ('N_A15_1', 'N_A17_3'), ('N_A17_3', 'N_O18_1'),
            ('N_O18_1', 'N_O19_1'), ('N_O19_1', 'N_A_D2'), ('N_A_D2', 'N_A20_3', 'Sim'), ('N_A20_3', 'N_C15_3'), ('N_A_D2', 'N_A20_1', 'Não'),
            ('N_A20_1', 'N_A22_1'), ('N_A22_1', 'N_A23_1'), ('N_A23_1', 'N_O24'), ('N_O24', 'N_O25'), ('N_O25', 'N_O26'), ('N_O26', 'N_O27')
        ]
        fases_nomes = [
            "1. Negociação de projeto", "2. Solicitação de Documentos", "3. Conferência documental", "4. Abertura processo PEN/SIE",
            "5. Aprovação do projeto no colegiado", "6. Aprovação PRA", "7. Análise pela equipe CT&I", "8. Assinatura contrato", "9. Projeto vigente"
        ]
        
        def avaliar_status(id_etapa):
            if id_etapa in ['N_V4', 'N_V5', 'N_C6', 'N_V7', 'N_V10', 'N_V11', 'N_V10_2_2', 'N_V_D1', 'N_V_D2', 'N_V_D3', 'N_V_SEGUIR']: return 11, 1
            elif id_etapa in ['N_V12', 'N_C13', 'N_V14_1', 'N_V14_2', 'N_A20_1', 'N_A20_3', 'N_A_D2']: return 22, 2
            elif id_etapa in ['N_A8', 'N_A15_1', 'N_C15_3', 'N_A9', 'N_A_D1']: return 33, 3
            elif id_etapa in ['N_INICIO', 'N_C1', 'N_C2', 'N_C3', 'N_C_D1']: return 44, 4
            elif id_etapa in ['N_C17_2_1', 'N_A17_3']: return 55, 5
            elif id_etapa in ['N_O18_1', 'N_O19_1', 'N_O24', 'N_O25', 'N_O26', 'N_O27']: return 66, 6
            elif id_etapa in ['N_J15_2_1', 'N_J15_2_2', 'N_J20_2_1', 'N_J21_2', 'N_PI16_2_1', 'N_PI18_2_1', 'N_PI19_2_1', 'N_V16_2_2', 'N_V16_2_3', 'N_V17_2_2', 'N_V18_2_2', 'N_V19_2_2', 'N_V20_2_2', 'N_J_D1', 'N_J_D2', 'N_J_D3', 'N_J_D4', 'N_V_D4']: return 77, 7
            elif id_etapa in ['N_A22_1', 'N_A23_1']: return 88, 8
            elif id_etapa in ['N_FIM', 'N_A_SEGUIR']: return 100, 9
            else: return 50, 5

    elif tipo_contrato == "Licenciamento":
        tradutor = {
            '1': 'L_NPV_1', '2': 'L_NPV_2', '3': 'L_NAP_1', '4': 'L_COM_1', '5': 'L_NAP_2', '6': 'L_PRA_1', '7': 'L_NAP_3',
            '8': 'L_NAP_4', '9': 'L_PRA_2', '10': 'L_NAP_5', '11': 'L_JUR_1', '12': 'L_NAP_6', '13': 'L_NAP_7', '14': 'L_CES_1',
            '15': 'L_NAP_8', '16': 'L_GEP_1', '17': 'L_GEP_2', '18': 'L_GEP_3', '19': 'L_NAP_9', '20': 'L_NAP_10'
        }
        textos = {
            'L_INICIO': 'Início', 'L_NPV_1': '1. Pedido de formalização de contrato', 'L_NPV_2': '2. Envia email: anexo dossiê',
            'L_NAP_1': '3. Abre processo', 'L_COM_1': '4. Anexa ata', 'L_NAP_2': '5. Minuta contrato', 'L_PRA_1': '6. Dispensa de Licitação',
            'L_NAP_3': '7. Publicação dispensa no DOU', 'L_NAP_4': '8. Declaração ausência / Doc empresa / Parecer', 'L_PRA_2': '9. Aprovação da formalização',
            'L_NAP_5': '10. Check-list / Certificado processual', 'L_JUR_1': '11. Análise PROJUR', 'L_NAP_6': '12. Coloca a Minuta contrato final',
            'L_NAP_7': '13. Após aprovação jurídico vamos para assinaturas', 'L_CES_1': '14. Para assinatura do Ofício', 'L_NAP_8': '15. Publicação DOU-Contrato',
            'L_GEP_1': '16. Ofício-Proinova-Progep', 'L_GEP_2': '17. Analisa / Recebe', 'L_GEP_3': '18. Anexa a Portaria gestores',
            'L_NAP_9': '19. Arquiva-se', 'L_NAP_10': '20. Informar as partes', 'L_FIM': 'Fim'
        }
        setores = {
            'NPV': ['L_INICIO', 'L_NPV_1', 'L_NPV_2'],
            'NAP': ['L_NAP_1', 'L_NAP_2', 'L_NAP_3', 'L_NAP_4', 'L_NAP_5', 'L_NAP_6', 'L_NAP_7', 'L_NAP_8', 'L_NAP_9', 'L_NAP_10', 'L_FIM'],
            'Comitê': ['L_COM_1'],
            'PRA': ['L_PRA_1', 'L_PRA_2'],
            'PROJUR': ['L_JUR_1'],
            'Cesar': ['L_CES_1'],
            'PROGEP': ['L_GEP_1', 'L_GEP_2', 'L_GEP_3']
        }
        conexoes = [
            ('L_INICIO', 'L_NPV_1'), ('L_NPV_1', 'L_NPV_2'), ('L_NPV_2', 'L_NAP_1'), ('L_NAP_1', 'L_COM_1'), ('L_COM_1', 'L_NAP_2'),
            ('L_NAP_2', 'L_PRA_1'), ('L_PRA_1', 'L_NAP_3'), ('L_NAP_3', 'L_NAP_4'), ('L_NAP_4', 'L_PRA_2'), ('L_PRA_2', 'L_NAP_5'),
            ('L_NAP_5', 'L_JUR_1'), ('L_JUR_1', 'L_NAP_6'), ('L_NAP_6', 'L_NAP_7'), ('L_NAP_7', 'L_CES_1'), ('L_CES_1', 'L_NAP_8'),
            ('L_NAP_8', 'L_GEP_1'), ('L_GEP_1', 'L_GEP_2'), ('L_GEP_2', 'L_GEP_3'), ('L_GEP_3', 'L_NAP_9'), ('L_NAP_9', 'L_NAP_10'), ('L_NAP_10', 'L_FIM')
        ]
        fases_nomes = [
            "1. Pedido e Dossiê (NPV)", "2. Abertura e Minuta", "3. Dispensa de Licitação", "4. Check-list e Aprovações",
            "5. Análise PROJUR", "6. Coleta de Assinaturas", "7. Publicação DOU", "8. Tramitação PROGEP", "9. Conclusão"
        ]
        
        def avaliar_status(id_etapa):
            if id_etapa in ['L_NPV_1', 'L_NPV_2']: return 11, 1
            elif id_etapa in ['L_NAP_1', 'L_COM_1', 'L_NAP_2']: return 22, 2
            elif id_etapa in ['L_PRA_1', 'L_NAP_3']: return 33, 3
            elif id_etapa in ['L_NAP_4', 'L_PRA_2', 'L_NAP_5']: return 44, 4
            elif id_etapa in ['L_JUR_1', 'L_NAP_6']: return 55, 5
            elif id_etapa in ['L_NAP_7', 'L_CES_1']: return 66, 6
            elif id_etapa in ['L_NAP_8']: return 77, 7
            elif id_etapa in ['L_GEP_1', 'L_GEP_2', 'L_GEP_3']: return 88, 8
            elif id_etapa in ['L_NAP_9', 'L_NAP_10', 'L_FIM']: return 100, 9
            else: return 50, 5

    return tradutor, textos, setores, conexoes, fases_nomes, avaliar_status

# ==========================================
# 4. ALGORITMOS DE BUSCA E CORES
# ==========================================
def encontrar_id_etapa(etapa_bruta, tradutor, textos):
    etapa_bruta = str(etapa_bruta).strip()
    if not etapa_bruta or etapa_bruta.lower() == 'nan': return ""
    
    if etapa_bruta in tradutor: return tradutor[etapa_bruta]
    for k in sorted(tradutor.keys(), key=len, reverse=True):
        if etapa_bruta.startswith(str(k)): return tradutor[k]
    for k, v in textos.items():
        if v.replace('\n', ' ').strip().lower() in etapa_bruta.lower(): return k
            
    return etapa_bruta

def obter_cor_progresso(porc):
    if porc <= 30: return '#F44336' 
    elif porc <= 60: return '#FF9800' 
    elif porc <= 90: return '#FBC02D' 
    else: return '#4CAF50' 

def obter_historico_concluido(etapa_atual, conexoes):
    if not etapa_atual: return set()
    grafo_reverso = {}
    for origem, destino, *resto in conexoes:
        if destino not in grafo_reverso: grafo_reverso[destino] = []
        grafo_reverso[destino].append(origem)
    
    completados = set()
    fila = [etapa_atual]
    while fila:
        atual = fila.pop(0)
        if atual not in completados:
            completados.add(atual)
            if atual in grafo_reverso:
                fila.extend(grafo_reverso[atual])
    if etapa_atual in completados: completados.remove(etapa_atual)
    return completados

# ==========================================
# 5. GERADORES DE GRÁFICOS DINÂMICOS
# ==========================================
def gerar_fluxograma_individual(etapa_destaque, textos, setores, conexoes):
    dot = graphviz.Digraph()
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.6', ranksep='0.6')
    dot.attr('node', margin='0.1,0.05', width='0', height='0')
    
    etapas_concluidas = obter_historico_concluido(etapa_destaque, conexoes)
    
    for nome_setor, lista_ids in setores.items():
        for id_caixa in lista_ids:
            texto_bruto = textos.get(id_caixa, id_caixa).replace('\n', ' ')
            texto_linhas = "\n".join(textwrap.wrap(texto_bruto, width=22))
            
            formato = 'box'
            if '?' in texto_bruto: formato = 'diamond'
            texto_exibicao = f"[{nome_setor.upper()}]\n{texto_linhas}" if id_caixa not in ['N_INICIO', 'N_FIM', 'L_INICIO', 'L_FIM'] else texto_linhas
            
            if id_caixa in ['N_INICIO', 'L_INICIO']: cor_fundo, cor_borda, cor_fonte = '#4CAF50', '#2E7D32', 'white'
            elif id_caixa in ['N_FIM', 'L_FIM']: cor_fundo, cor_borda, cor_fonte = '#F44336', '#C62828', 'white'
            elif id_caixa == etapa_destaque: cor_fundo, cor_borda, cor_fonte = '#FFF176', '#F57F17', 'black' 
            elif id_caixa in etapas_concluidas: cor_fundo, cor_borda, cor_fonte = '#C8E6C9', '#2E7D32', 'black'
            else: cor_fundo, cor_borda, cor_fonte = '#FFFFFF', '#90A4AE', 'black'
            
            if id_caixa in ['N_INICIO', 'N_FIM', 'L_INICIO', 'L_FIM']:
                dot.node(id_caixa, texto_exibicao, shape='circle', style='filled', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth='3', fontname='Helvetica-Bold', fontsize='24')
            elif id_caixa == etapa_destaque:
                dot.node(id_caixa, texto_exibicao, shape=formato, style='filled, rounded, bold', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth='6', fontname='Helvetica-Bold', fontsize='22')
                dot.node('MARKER', '📍 ETAPA ATUAL', shape='box', style='filled, rounded', fillcolor='#D32F2F', color='#B71C1C', fontcolor='white', penwidth='2', fontname='Helvetica-Bold', fontsize='14', margin='0.1')
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.edge(id_caixa, 'MARKER', dir='back', color='#D32F2F', penwidth='3.0', arrowtail='vee', minlen='2')
            else:
                dot.node(id_caixa, texto_exibicao, shape=formato, style='filled, rounded', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth='2', fontname='Helvetica-Bold', fontsize='18')

    for conexao in conexoes:
        if len(conexao) == 3: dot.edge(conexao[0], conexao[1], label=f" {conexao[2]} ", fontsize='16', fontname='Helvetica-Bold', fontcolor='#1976D2', color='#90A4AE', penwidth='2.0')
        else: dot.edge(conexao[0], conexao[1], color='#90A4AE', penwidth='2.0')

    return dot

def gerar_minimapa_individual(etapa_destaque, setores, conexoes):
    dot = graphviz.Digraph()
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.15', ranksep='0.15', size='3,3')
    dot.attr('node', label='', shape='box', style='filled', width='0.3', height='0.15', margin='0')
    
    etapas_concluidas = obter_historico_concluido(etapa_destaque, conexoes)
    
    for nome_setor, lista_ids in setores.items():
        for id_caixa in lista_ids:
            if id_caixa in ['N_INICIO', 'L_INICIO']: dot.node(id_caixa, shape='circle', fillcolor='#4CAF50', color='#4CAF50', width='0.2', height='0.2')
            elif id_caixa in ['N_FIM', 'L_FIM']: dot.node(id_caixa, shape='circle', fillcolor='#F44336', color='#F44336', width='0.2', height='0.2')
            elif id_caixa == etapa_destaque:
                dot.node(id_caixa, shape='circle', fillcolor='#FF2020', color='#900000', width='0.5', height='0.5', penwidth='2')
                dot.node('MARKER_MINI', 'ATUAL', shape='plaintext', fontcolor='#D32F2F', fontsize='12', fontname='Helvetica-Bold')
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.edge(id_caixa, 'MARKER_MINI', dir='back', color='#D32F2F', penwidth='2.0', arrowtail='vee', minlen='1')
            elif id_caixa in etapas_concluidas: dot.node(id_caixa, fillcolor='#C8E6C9', color='#A5D6A7') 
            else: dot.node(id_caixa, fillcolor='#E0E0E0', color='#B0BEC5') 
                
    for conexao in conexoes:
        dot.edge(conexao[0], conexao[1], color='#CFD8DC', penwidth='1.0', arrowsize='0.3')
        
    return dot

def gerar_fluxograma_geral(df_dados, tradutor, textos, setores, conexoes):
    dot = graphviz.Digraph()
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='0.8')
    dot.attr('node', margin='0.1,0.05', width='0', height='0')
    
    projetos_na_etapa = {}
    for index, row in df_dados.iterrows():
        etapa_bruta = str(row['Etapa_Atual']).strip().replace('.0', '')
        reg = str(row['Registro']).replace('.0', '')
        coord = str(row['Coordenador']).strip()
        if coord.lower() == 'nan' or coord == '': coord = 'Sem Nome'
        if not reg or reg == 'nan': continue
        
        id_et = encontrar_id_etapa(etapa_bruta, tradutor, textos)
        if id_et not in projetos_na_etapa: projetos_na_etapa[id_et] = []
        projetos_na_etapa[id_et].append(f"{reg} - {coord}")

    for nome_setor, lista_ids in setores.items():
        for id_caixa in lista_ids:
            texto_bruto = textos.get(id_caixa, id_caixa).replace('\n', ' ')
            texto_linhas = "\n".join(textwrap.wrap(texto_bruto, width=22))
            
            formato = 'box'
            if '?' in texto_bruto: formato = 'diamond'
            texto_exibicao = f"[{nome_setor.upper()}]\n{texto_linhas}" if id_caixa not in ['N_INICIO', 'N_FIM', 'L_INICIO', 'L_FIM'] else texto_linhas
            
            cor_fundo, cor_borda, cor_fonte = '#FFFFFF', '#90A4AE', 'black'
            penwidth = '2'
            
            if id_caixa in ['N_INICIO', 'L_INICIO']: cor_fundo, cor_borda, cor_fonte = '#4CAF50', '#2E7D32', 'white'
            elif id_caixa in ['N_FIM', 'L_FIM']: cor_fundo, cor_borda, cor_fonte = '#F44336', '#C62828', 'white'
            
            if id_caixa in projetos_na_etapa:
                cor_borda = '#D32F2F'
                penwidth = '4'
            
            dot.node(id_caixa, texto_exibicao, shape=formato if id_caixa not in ['N_INICIO', 'N_FIM', 'L_INICIO', 'L_FIM'] else 'circle', style='filled, rounded' if id_caixa not in ['N_INICIO', 'N_FIM', 'L_INICIO', 'L_FIM'] else 'filled', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth=penwidth, fontname='Helvetica-Bold', fontsize='18' if id_caixa not in ['N_INICIO', 'N_FIM', 'L_INICIO', 'L_FIM'] else '24')

            if id_caixa in projetos_na_etapa:
                lista_prjs = projetos_na_etapa[id_caixa]
                max_exibir = 10 
                
                linhas_html = ""
                for prj in lista_prjs[:max_exibir]:
                    linhas_html += f'<TR><TD BGCOLOR="#FFEBEE" BORDER="1" COLOR="#D32F2F" ALIGN="LEFT"><FONT POINT-SIZE="11" COLOR="#C62828"><b>{prj}</b></FONT></TD></TR>'
                if len(lista_prjs) > max_exibir:
                    linhas_html += f'<TR><TD BGCOLOR="#FFCDD2" BORDER="1" COLOR="#D32F2F" ALIGN="CENTER"><FONT POINT-SIZE="11" COLOR="#C62828"><b>➕ ... e mais {len(lista_prjs) - max_exibir} projetos</b></FONT></TD></TR>'

                marker_html = f"""<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2" CELLPADDING="4"><TR><TD ALIGN="CENTER"><FONT COLOR="#D32F2F" POINT-SIZE="11"><b>PROCESSOS AQUI:</b></FONT></TD></TR>{linhas_html}</TABLE>>"""
                nome_marker = f'MARKER_{id_caixa}'
                dot.node(nome_marker, marker_html, shape='plaintext')
                
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.edge(id_caixa, nome_marker, dir='back', color='#D32F2F', penwidth='2.5', arrowtail='vee', minlen='1')

    for conexao in conexoes:
        if len(conexao) == 3: dot.edge(conexao[0], conexao[1], label=f" {conexao[2]} ", fontsize='14', fontname='Helvetica-Bold', fontcolor='#1976D2', color='#B0BEC5', penwidth='1.5')
        else: dot.edge(conexao[0], conexao[1], color='#B0BEC5', penwidth='1.5')

    return dot

def gerar_minimapa_nap(df_dados, tradutor, textos, setores, conexoes):
    dot = graphviz.Digraph()
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.25', ranksep='0.25')
    dot.attr('node', label='', shape='box', style='filled', width='0.3', height='0.15', margin='0')
    
    projetos_na_etapa = {}
    for index, row in df_dados.iterrows():
        etapa_bruta = str(row['Etapa_Atual']).strip().replace('.0', '')
        reg = str(row['Registro']).replace('.0', '')
        if not reg or reg == 'nan': continue
        id_et = encontrar_id_etapa(etapa_bruta, tradutor, textos)
        if id_et not in projetos_na_etapa: projetos_na_etapa[id_et] = 0
        projetos_na_etapa[id_et] += 1
        
    for nome_setor, lista_ids in setores.items():
        for id_caixa in lista_ids:
            if id_caixa in ['N_INICIO', 'L_INICIO']: dot.node(id_caixa, shape='circle', fillcolor='#4CAF50', color='#4CAF50', width='0.2', height='0.2')
            elif id_caixa in ['N_FIM', 'L_FIM']: dot.node(id_caixa, shape='circle', fillcolor='#F44336', color='#F44336', width='0.2', height='0.2')
            elif id_caixa in projetos_na_etapa:
                dot.node(id_caixa, fillcolor='#FFCDD2', color='#D32F2F', penwidth='2')
                qtd = projetos_na_etapa[id_caixa]
                texto = f"{qtd} PROJETO{'S' if qtd>1 else ''}"
                nome_marker = f'MINIMARKER_{id_caixa}'
                dot.node(nome_marker, texto, shape='box', style='filled, rounded', fillcolor='#FFFFFF', color='#D32F2F', fontcolor='#C62828', penwidth='1.5', fontname='Helvetica-Bold', fontsize='10', width='0', height='0', margin='0.05')
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.edge(id_caixa, nome_marker, dir='back', color='#D32F2F', penwidth='1.5', arrowtail='vee', minlen='1')
            else:
                dot.node(id_caixa, fillcolor='#E0E0E0', color='#B0BEC5')
                
    for conexao in conexoes:
        dot.edge(conexao[0], conexao[1], color='#CFD8DC', penwidth='1.0', arrowsize='0.3')
        
    return dot

# ==========================================
# 6. NAVEGAÇÃO E EXECUÇÃO
# ==========================================
st.sidebar.title("Navegação do Sistema")
modo_visao = st.sidebar.radio("Módulo:", ["🌎 Consulta Pública", "⚙️ Visão Interna (Equipe NAP)"])
st.sidebar.markdown("---")

if modo_visao == "🌎 Consulta Pública":
    st.title("Rastreamento de Projetos")
    
    tipo_contrato = st.selectbox("Selecione a modalidade do contrato:", ["Acordo de Parceria", "Licenciamento"])
    
    trad_et, txts, setr, cnxs, fases, func_aval = carregar_modelo_contrato(tipo_contrato)
    
    busca = st.text_input("Buscar Projeto (Ex: 066335 ou Nome do Projeto)").strip()
    if busca:
        projeto = df[(df['Registro'].str.contains(busca, case=False, na=False)) | (df['Titulo'].str.contains(busca, case=False, na=False))]
                     
        if not projeto.empty:
            num_projeto = str(projeto.iloc[0]['Registro']).replace('.0', '')
            tit_projeto = str(projeto.iloc[0]['Titulo'])
            etapa_bruta = str(projeto.iloc[0]['Etapa_Atual']).strip().replace('.0', '')
            
            id_etapa = encontrar_id_etapa(etapa_bruta, trad_et, txts)
            porcentagem, etapa_macro = func_aval(id_etapa)
            cor_barra = obter_cor_progresso(porcentagem)
            
            st.sidebar.markdown(f"""<style>.stProgress > div > div > div > div {{background-color: {cor_barra} !important;}}</style>""", unsafe_allow_html=True)
            
            st.sidebar.title("📊 Painel do Projeto")
            st.sidebar.markdown(f"### Nº {num_projeto}")
            st.sidebar.markdown(f"**{tit_projeto}**")
            st.sidebar.progress(porcentagem / 100, text=f"Progresso: {porcentagem}% Concluído")
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🗺️ Posição Global")
            minimapa = gerar_minimapa_individual(id_etapa, setr, cnxs)
            st.sidebar.graphviz_chart(minimapa, use_container_width=True)
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📍 Linha do Tempo")
            for i, nome_fase in enumerate(fases, 1):
                if i < etapa_macro: st.sidebar.markdown(f"<div style='background-color:#E8F5E9; color:#2E7D32; padding:10px; border-radius:5px; margin-bottom:8px; border-left:4px solid #4CAF50;'><b>✅ {nome_fase}</b></div>", unsafe_allow_html=True)
                elif i == etapa_macro: st.sidebar.markdown(f"<div style='background-color:#FFF9C4; color:#F57F17; padding:10px; border-radius:5px; margin-bottom:8px; border-left:4px solid #FBC02D; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);'><b>⏳ {nome_fase}</b></div>", unsafe_allow_html=True)
                else: st.sidebar.markdown(f"<div style='background-color:#FFFFFF; color:#9E9E9E; padding:10px; border-radius:5px; margin-bottom:8px; border:1px solid #E0E0E0;'><b>🔒 {nome_fase}</b></div>", unsafe_allow_html=True)

            grafico = gerar_fluxograma_individual(id_etapa, txts, setr, cnxs)
            st.graphviz_chart(grafico, use_container_width=False) 
        else:
            st.warning("Projeto não encontrado.")

elif modo_visao == "⚙️ Visão Interna (Equipe NAP)":
    st.title("Painel de Gestão de Contratos")
    
    if not st.session_state['nap_autenticado']:
        senha_digitada = st.text_input("🔑 Digite a senha de acesso (NAP):", type="password")
        if senha_digitada == "nap2026":
            st.session_state['nap_autenticado'] = True
            st.rerun() 
        elif senha_digitada != "":
            st.error("Senha incorreta. Acesso negado.")
            
    else: 
        col1, col2 = st.columns([8, 2])
        col1.success("Acesso Liberado! Visão administrativa ativa.")
        if col2.button("🔒 Bloquear Painel"):
            st.session_state['nap_autenticado'] = False
            st.rerun()
            
        st.markdown("---")
        tipo_contrato_nap = st.selectbox("Selecione o Dashboard Gerencial:", ["Acordo de Parceria", "Licenciamento"], key="dropdown_interno")
        
        trad_et, txts, setr, cnxs, fases, func_aval = carregar_modelo_contrato(tipo_contrato_nap)
        
        df_validos = df[df['Registro'] != ''].copy()
        total_projetos = len(df_validos)
        
        contagem_macro = {i: 0 for i in range(1, 10)}
        for _, row in df_validos.iterrows():
            etapa_bruta = str(row['Etapa_Atual']).strip().replace('.0', '')
            id_etapa = encontrar_id_etapa(etapa_bruta, trad_et, txts)
            _, fase_num = func_aval(id_etapa)
            if fase_num in contagem_macro:
                contagem_macro[fase_num] += 1
        
        st.sidebar.title("📊 Resumo Macro")
        st.sidebar.markdown(f"**Total Ativos:** {total_projetos} projetos ({tipo_contrato_nap})")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🗺️ Mapa de Calor")
        minimapa_nap = gerar_minimapa_nap(df_validos, trad_et, txts, setr, cnxs)
        st.sidebar.graphviz_chart(minimapa_nap, use_container_width=True)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📍 Linha do Tempo Geral")
        for i, nome_fase in enumerate(fases, 1):
            qtd = contagem_macro[i]
            if qtd > 0: st.sidebar.markdown(f"<div style='background-color:#FFEBEE; color:#C62828; padding:8px; border-radius:5px; margin-bottom:5px; border-left:4px solid #D32F2F;'><b>{qtd} projetos</b> - {nome_fase}</div>", unsafe_allow_html=True)
            else: st.sidebar.markdown(f"<div style='background-color:#F5F5F5; color:#9E9E9E; padding:8px; border-radius:5px; margin-bottom:5px; border-left:4px solid #9E9E9E;'><b>0 projetos</b> - {nome_fase}</div>", unsafe_allow_html=True)
        
        st.write(f"Monitorando o detalhamento de processos ({tipo_contrato_nap}):")
        grafico_macro = gerar_fluxograma_geral(df_validos, trad_et, txts, setr, cnxs)
        st.graphviz_chart(grafico_macro, use_container_width=False)
        
        st.markdown("---")
        st.markdown("### 📋 Base de Dados Completa")
        
        df_resumo = df_validos.copy()
        df_resumo['Fase Atual'] = df_resumo['Etapa_Atual'].apply(lambda x: txts.get(encontrar_id_etapa(str(x).strip().replace('.0',''), trad_et, txts), "Não identificada").replace('\n', ' '))
        
        csv_dados = df_resumo[['Registro', 'Titulo', 'Coordenador', 'Fase Atual']].to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Baixar Planilha (Excel/CSV)", data=csv_dados, file_name=f'Projetos_{tipo_contrato_nap}.csv', mime='text/csv')
        
        st.dataframe(df_resumo[['Registro', 'Titulo', 'Coordenador', 'Fase Atual']], use_container_width=True, hide_index=True)
