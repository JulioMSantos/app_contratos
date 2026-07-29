import streamlit as st
import pandas as pd
import graphviz
import textwrap

st.set_page_config(layout="wide", page_title="Sistema Integra", page_icon="📊")

# Inicializa a "Memória" do sistema para a senha do NAP
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
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
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
    
    # Adicionamos a busca pela coluna do Coordenador
    df = df_bruto.rename(columns={
        'Registro Portal de Projetos': 'Registro',
        'Projeto/Título': 'Titulo',
        'Etapa Atual': 'Etapa_Atual',
        'Coordenador': 'Coordenador' # Se na sua planilha estiver diferente (Ex: 'Coordenador(a)'), mude aqui a primeira palavra
    })
    
    colunas_essenciais = ['Registro', 'Titulo', 'Etapa_Atual', 'Coordenador']
    faltaram = [col for col in colunas_essenciais if col not in df.columns]
    if faltaram:
        for col in faltaram:
            df[col] = "" 
            
    df['Registro'] = df['Registro'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['Titulo'] = df['Titulo'].astype(str).str.strip()
    df['Etapa_Atual'] = df['Etapa_Atual'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['Coordenador'] = df['Coordenador'].astype(str).str.strip()

except Exception as e:
    df = pd.DataFrame(columns=['Registro', 'Titulo', 'Etapa_Atual', 'Coordenador'])

# ==========================================
# 3. DICIONÁRIOS DO FLUXOGRAMA
# ==========================================
tradutor_etapas = {
    '1': 'N_C1', '2': 'N_C2', '3': 'N_C3', '4': 'N_V4', '5': 'N_V5',
    '6': 'N_C6', '7': 'N_V7', '8': 'N_A8', '9': 'N_A9', '10': 'N_V10',
    '11': 'N_V11', '12': 'N_V12', '13': 'N_C13', '14.1': 'N_V14_1',
    '14.2': 'N_V14_2', '15.1': 'N_A15_1', '15.2.1': 'N_J15_2_1',
    '15.2.2': 'N_J15_2_2', '15.3': 'N_C15_3', '16.2.1': 'N_PI16_2_1',
    '16.2.2': 'N_V16_2_2', '16.2.3': 'N_V16_2_3', '17.2.1': 'N_C17_2_1',
    '17.2.2': 'N_V17_2_2', '17.3': 'N_A17_3', '18.1': 'N_O18_1',
    '18.2.1': 'N_PI18_2_1', '18.2.2': 'N_V18_2_2', '19.1': 'N_O19_1',
    '19.2.1': 'N_PI19_2_1', '19.2.2': 'N_V19_2_2', '20.1': 'N_A20_1',
    '20.2.1': 'N_J20_2_1', '20.2.2': 'N_V20_2_2', '20.3': 'N_A20_3',
    '21.2': 'N_J21_2', '22.1': 'N_A22_1', '23.1': 'N_A23_1',
    '24': 'N_O24', '25': 'N_O25', '26': 'N_O26', '27': 'N_O27'
}

textos = {
    'N_INICIO': 'Início', 'N_C1': '1. Abrir processo no PEN\ne preencher formulário',
    'N_C_D1': 'Algum documento\npreviamente acordado?', 'N_C2': '2. Anexar ao Processo PEN',
    'N_C3': '3. Tramitar para o NPV', 'N_C6': '6. Elaborar a proposta\ninicial para a Empresa',
    'N_C13': '13. Responder o e-mail', 'N_C15_3': '15.3 Enviar documentação\npreenchida',
    'N_C17_2_1': '17.2.1 Preencher declaração\ne enviar ao NPI', 'N_V4': '4. Realizar reunião de\ncomunicação do projeto',
    'N_V5': '5. Enviar material\ninformativo', 'N_V_D1': 'Precisa determinar a\ndivisão de PI?',
    'N_V_D2': 'Precisa valorar?', 'N_V10_2_2': '10.2.2 Valoração',
    'N_V_SEGUIR': 'Seguir independentemente', 'N_V_D3': 'Negociação pela NPV?',
    'N_V10': '10. Negociar e fechar\na proposta', 'N_V11': '11. Tramitar para o NAP',
    'N_V7': '7. Analisar e Tramitar\npara o NAP', 'N_V12': '12. Enviar modelo de e-mail\n"Escolha Fundação"',
    'N_V14_1': '14.1 Enviar a documentação\npara instrução processual', 'N_V14_2': '14.2 Encaminhar a demanda\nao jurídico por e-mail',
    'N_V_D4': 'Qual o tipo de\nnegociação de TT?', 'N_V16_2_3': '16.2.3 Negociar as\ncláusulas do contrato',
    'N_V20_2_2': '20.2.2 Emitir relatório\nde negociação', 'N_V16_2_2': '16.2.2 Valoração',
    'N_V17_2_2': '17.2.2 Emitir relatório\ntécnico de valoração', 'N_V18_2_2': '18.2.2 Emitir parecer\nde valoração',
    'N_V19_2_2': '19.2.2 Enviar para\no Jurídico', 'N_A8': '8. Analisar e\nEnquadramento',
    'N_A_D1': 'É um Acordo de parceria?', 'N_A_SEGUIR': 'Seguir conforme o\nenquadramento',
    'N_FIM': 'FIM', 'N_A9': '9. Tramitar para o NPV',
    'N_A15_1': '15.1 Analisar a\ndocumentação', 'N_A17_3': '17.3 Encaminhar por e-mail\npara análise da PRA',
    'N_A_D2': 'Documentação precisa\nde correção?', 'N_A20_3': '20.3 Retornar por e-mail\nao coordenador',
    'N_A20_1': '20.1 Anexar documentos\ne solicitar Fundação', 'N_A22_1': '22.1 Coletar assinaturas',
    'N_A23_1': '23.1 Tramitar para a PRA', 'N_J_D1': 'Empresa tem\nprópria minuta?',
    'N_J15_2_1': '15.2.1 Analisar minuta\nencaminhada', 'N_J15_2_2': '15.2.2 Encaminhar minuta\npadrão AGU',
    'N_J_D2': '16.2.1 Tem questões de\ndivisão de PI?', 'N_J_D3': 'Tem questões para\nnegociar de TT?',
    'N_J20_2_1': '20.2.1 Elaborar a minuta', 'N_J21_2': '21.2 Fechar a minuta',
    'N_J_D4': 'Precisa quadro comparativo?', 'N_PI16_2_1': '16.2.1 Encaminhar e-mail\ndeclaração de atividades',
    'N_PI18_2_1': '18.2.1 Definir percentual de PI\ne emitir parecer', 'N_PI19_2_1': '19.2.1 Encaminhar e-mail\npara Empresa, Coord e Jurídico',
    'N_O18_1': '18.1 Analisar a\ndocumentação (PRA)', 'N_O19_1': '19.1 Enviar por e-mail\npara o NAP (PRA)',
    'N_O24': '24. Realizar análise (PRA)', 'N_O25': '25. Emitir parecer (PRA)',
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
    ('N_INICIO', 'N_C1'), ('N_C1', 'N_C_D1'),
    ('N_C_D1', 'N_C2', 'Sim'), ('N_C_D1', 'N_C3', 'Não'),
    ('N_C2', 'N_C3'), ('N_C3', 'N_V4'), ('N_V4', 'N_V5'),
    ('N_V5', 'N_V_D1'), ('N_V_D1', 'N_C6', 'Sim'), ('N_C6', 'N_V7'),
    ('N_V_D1', 'N_V_D2', 'Não'), ('N_V_D2', 'N_V10_2_2', 'Sim'), 
    ('N_V_D2', 'N_V_SEGUIR', 'Não'), ('N_V10_2_2', 'N_V_D3'), 
    ('N_V_SEGUIR', 'N_V_D3'), ('N_V_D3', 'N_V10', 'Sim'), 
    ('N_V10', 'N_V11'), ('N_V_D3', 'N_V7', 'Não'), 
    ('N_V11', 'N_A8'), ('N_V7', 'N_A8'), ('N_A8', 'N_A_D1'), 
    ('N_A_D1', 'N_A_SEGUIR', 'Não'), ('N_A_SEGUIR', 'N_FIM'),
    ('N_A_D1', 'N_A9', 'Sim'), ('N_A9', 'N_V12'), ('N_V12', 'N_C13'),
    ('N_C13', 'N_V14_1'), ('N_V14_1', 'N_C15_3'), ('N_C15_3', 'N_V14_2'),
    ('N_V14_2', 'N_J_D1'), ('N_V14_2', 'N_A15_1'),
    ('N_J_D1', 'N_J15_2_1', 'Sim'), ('N_J_D1', 'N_J15_2_2', 'Não'),
    ('N_J15_2_1', 'N_J_D2'), ('N_J15_2_2', 'N_J_D2'),
    ('N_J_D2', 'N_PI16_2_1', 'Sim'), ('N_PI16_2_1', 'N_C17_2_1'), 
    ('N_C17_2_1', 'N_PI18_2_1'), ('N_PI18_2_1', 'N_PI19_2_1'), 
    ('N_PI19_2_1', 'N_J20_2_1'), ('N_J_D2', 'N_J_D3', 'Não'),
    ('N_J_D3', 'N_J20_2_1', 'Não'), ('N_J_D3', 'N_V_D4', 'Sim'),
    ('N_V_D4', 'N_V16_2_3', 'Diferentes'), ('N_V16_2_3', 'N_V20_2_2'), 
    ('N_V20_2_2', 'N_J20_2_1'), ('N_V_D4', 'N_V16_2_2', 'Valoração'), 
    ('N_V16_2_2', 'N_V17_2_2'), ('N_V17_2_2', 'N_V18_2_2'), 
    ('N_V18_2_2', 'N_V19_2_2'), ('N_V19_2_2', 'N_J20_2_1'),
    ('N_J20_2_1', 'N_J21_2'), ('N_J21_2', 'N_J_D4'),
    ('N_A15_1', 'N_A17_3'), ('N_A17_3', 'N_O18_1'), ('N_O18_1', 'N_O19_1'),
    ('N_O19_1', 'N_A_D2'), ('N_A_D2', 'N_A20_3', 'Sim'), 
    ('N_A20_3', 'N_C15_3'), ('N_A_D2', 'N_A20_1', 'Não'), 
    ('N_A20_1', 'N_A22_1'), ('N_A22_1', 'N_A23_1'),
    ('N_A23_1', 'N_O24'), ('N_O24', 'N_O25'), ('N_O25', 'N_O26'), 
    ('N_O26', 'N_O27')
]

# ==========================================
# 4. ALGORITMOS BASE
# ==========================================
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

def obter_historico_concluido(etapa_atual):
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
# 5. GERADOR INDIVIDUAL (VISÃO PÚBLICA)
# ==========================================
def gerar_fluxograma_individual(etapa_destaque=None):
    dot = graphviz.Digraph(comment='Fluxograma Individual')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.6', ranksep='0.6')
    dot.attr('node', margin='0.1,0.05', width='0', height='0')
    
    etapas_concluidas = obter_historico_concluido(etapa_destaque)
    
    for nome_setor, lista_ids in setores.items():
        for id_caixa in lista_ids:
            texto_bruto = textos.get(id_caixa, id_caixa).replace('\n', ' ')
            texto_linhas = "\n".join(textwrap.wrap(texto_bruto, width=22))
            
            formato = 'box'
            if '?' in texto_bruto: formato = 'diamond'
            
            texto_exibicao = f"[{nome_setor.upper()}]\n{texto_linhas}" if id_caixa not in ['N_INICIO', 'N_FIM'] else texto_linhas
            
            if id_caixa == 'N_INICIO': cor_fundo, cor_borda, cor_fonte = '#4CAF50', '#2E7D32', 'white'
            elif id_caixa == 'N_FIM': cor_fundo, cor_borda, cor_fonte = '#F44336', '#C62828', 'white'
            elif id_caixa == etapa_destaque: cor_fundo, cor_borda, cor_fonte = '#FFD700', '#B8860B', 'black'
            elif id_caixa in etapas_concluidas: cor_fundo, cor_borda, cor_fonte = '#C8E6C9', '#2E7D32', 'black'
            else: cor_fundo, cor_borda, cor_fonte = '#FFFFFF', '#90A4AE', 'black'
            
            if id_caixa in ['N_INICIO', 'N_FIM']:
                dot.node(id_caixa, texto_exibicao, shape='circle', style='filled', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth='3', fontname='Helvetica-Bold', fontsize='24')
            elif id_caixa == etapa_destaque:
                dot.node(id_caixa, texto_exibicao, shape=formato, style='filled, rounded', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth='5', fontname='Helvetica-Bold', fontsize='22')
                dot.node('MARKER', 'ATUAL', shape='plaintext', fontcolor='#D32F2F', fontsize='16', fontname='Helvetica-Bold')
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.edge(id_caixa, 'MARKER', dir='back', color='#1A1C23', penwidth='3.0', arrowtail='vee', minlen='2')
            else:
                dot.node(id_caixa, texto_exibicao, shape=formato, style='filled, rounded', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth='2', fontname='Helvetica-Bold', fontsize='18')

    for conexao in conexoes:
        origem, destino = conexao[0], conexao[1]
        cor_seta = '#90A4AE'
        if len(conexao) == 3: dot.edge(origem, destino, label=f" {conexao[2]} ", fontsize='16', fontname='Helvetica-Bold', fontcolor='#1976D2', color=cor_seta, penwidth='2.0')
        else: dot.edge(origem, destino, color=cor_seta, penwidth='2.0')

    return dot

# ==========================================
# 6. GERADOR GERAL (VISÃO INTERNA NAP)
# ==========================================
def gerar_fluxograma_geral(df_dados):
    dot = graphviz.Digraph(comment='Fluxograma Administrativo')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='0.8')
    dot.attr('node', margin='0.1,0.05', width='0', height='0')
    
    projetos_na_etapa = {}
    for index, row in df_dados.iterrows():
        etapa_bruta = str(row['Etapa_Atual']).strip().replace('.0', '')
        reg = str(row['Registro']).replace('.0', '')
        
        # Pega o Coordenador (trata casos vazios ou 'nan')
        coord = str(row['Coordenador']).strip()
        if coord.lower() == 'nan' or coord == '': 
            coord = 'Sem Nome'
            
        if not reg or reg == 'nan': continue
        
        id_et = tradutor_etapas.get(etapa_bruta, etapa_bruta)
        if id_et not in projetos_na_etapa:
            projetos_na_etapa[id_et] = []
            
        # O texto do Marca-Páginas agora é "Número - Coordenador"
        texto_etiqueta = f"{reg} - {coord}"
        projetos_na_etapa[id_et].append(texto_etiqueta)

    for nome_setor, lista_ids in setores.items():
        for id_caixa in lista_ids:
            texto_bruto = textos.get(id_caixa, id_caixa).replace('\n', ' ')
            texto_linhas = "\n".join(textwrap.wrap(texto_bruto, width=22))
            
            formato = 'box'
            if '?' in texto_bruto: formato = 'diamond'
            texto_exibicao = f"[{nome_setor.upper()}]\n{texto_linhas}" if id_caixa not in ['N_INICIO', 'N_FIM'] else texto_linhas
            
            cor_fundo, cor_borda, cor_fonte = '#FFFFFF', '#90A4AE', 'black'
            penwidth = '2'
            
            if id_caixa == 'N_INICIO': cor_fundo, cor_borda, cor_fonte = '#4CAF50', '#2E7D32', 'white'
            elif id_caixa == 'N_FIM': cor_fundo, cor_borda, cor_fonte = '#F44336', '#C62828', 'white'
            
            if id_caixa in projetos_na_etapa:
                cor_borda = '#D32F2F'
                penwidth = '4'
            
            dot.node(id_caixa, texto_exibicao, shape=formato if id_caixa not in ['N_INICIO', 'N_FIM'] else 'circle', style='filled, rounded' if id_caixa not in ['N_INICIO', 'N_FIM'] else 'filled', fillcolor=cor_fundo, color=cor_borda, fontcolor=cor_fonte, penwidth=penwidth, fontname='Helvetica-Bold', fontsize='18' if id_caixa not in ['N_INICIO', 'N_FIM'] else '24')

            if id_caixa in projetos_na_etapa:
                lista_prjs = projetos_na_etapa[id_caixa]
                
                linhas_html = ""
                for prj in lista_prjs:
                    # Fonte 12 para garantir que "000000 - Nome Longo" caiba de forma elegante
                    linhas_html += f'<TR><TD BGCOLOR="#FFEBEE" BORDER="1" COLOR="#D32F2F" ALIGN="LEFT" PORT="{prj}"><FONT POINT-SIZE="12" COLOR="#C62828"><b>{prj}</b></FONT></TD></TR>'
                
                marker_html = f"""<
                <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2" CELLPADDING="4">
                    <TR><TD ALIGN="CENTER"><FONT COLOR="#D32F2F" POINT-SIZE="11"><b>PROJETOS NESTA ETAPA:</b></FONT></TD></TR>
                    {linhas_html}
                </TABLE>>"""
                
                nome_marker = f'MARKER_{id_caixa}'
                dot.node(nome_marker, marker_html, shape='plaintext')
                
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.edge(id_caixa, nome_marker, dir='back', color='#D32F2F', penwidth='2.5', arrowtail='vee', minlen='1')

    for conexao in conexoes:
        origem, destino = conexao[0], conexao[1]
        cor_seta = '#B0BEC5'
        if len(conexao) == 3: dot.edge(origem, destino, label=f" {conexao[2]} ", fontsize='14', fontname='Helvetica-Bold', fontcolor='#1976D2', color=cor_seta, penwidth='1.5')
        else: dot.edge(origem, destino, color=cor_seta, penwidth='1.5')

    return dot

# ==========================================
# 7. ESTRUTURA DO APLICATIVO EM ABAS
# ==========================================
aba_publica, aba_nap = st.tabs(["🌎 Consulta Pública", "⚙️ Visão Interna (Equipe NAP)"])

# ----------------- ABA PÚBLICA -----------------
with aba_publica:
    st.subheader("Rastreamento de Projetos")
    
    # O Dropdown da Visão Pública ATUALIZADO COM PROTOCOLO DE INTENÇÕES
    tipo_contrato = st.selectbox(
        "Selecione a modalidade do contrato:", 
        ["Acordo de Parceria", "Protocolo de Intenções (Em Breve)", "ACT (Em Breve)", "Contrato global (Em Breve)"]
    )
    
    if tipo_contrato == "Acordo de Parceria":
        busca = st.text_input("Buscar Projeto (Ex: 066335 ou Nome do Projeto)").strip()

        if busca:
            projeto = df[(df['Registro'].str.contains(busca, case=False, na=False)) | 
                         (df['Titulo'].str.contains(busca, case=False, na=False))]
                         
            if not projeto.empty:
                num_projeto = str(projeto.iloc[0]['Registro']).replace('.0', '')
                tit_projeto = str(projeto.iloc[0]['Titulo'])
                etapa_bruta = str(projeto.iloc[0]['Etapa_Atual']).strip().replace('.0', '')
                
                id_etapa = tradutor_etapas.get(etapa_bruta, etapa_bruta)
                porcentagem, etapa_macro = avaliar_status(id_etapa)
                
                st.sidebar.title("📊 Painel do Projeto")
                st.sidebar.markdown(f"### Nº {num_projeto}")
                st.sidebar.markdown(f"**{tit_projeto}**")
                st.sidebar.progress(porcentagem / 100, text=f"Progresso: {porcentagem}% Concluído")
                st.sidebar.markdown("---")
                
                fases_nomes = [
                    "1. Negociação de projeto", "2. Solicitação de Documentos",
                    "3. Conferência documental", "4. Abertura processo PEN/SIE",
                    "5. Aprovação do projeto no colegiado", "6. Aprovação PRA",
                    "7. Análise pela equipe CT&I", "8. Assinatura contrato", "9. Projeto vigente"
                ]
                
                st.sidebar.markdown("### 📍 Linha do Tempo")
                for i, nome_fase in enumerate(fases_nomes, 1):
                    if i < etapa_macro:
                        st.sidebar.markdown(f"<div style='background-color:#E8F5E9; color:#2E7D32; padding:10px; border-radius:5px; margin-bottom:8px; border-left:4px solid #4CAF50;'><b>✅ {nome_fase}</b></div>", unsafe_allow_html=True)
                    elif i == etapa_macro:
                        st.sidebar.markdown(f"<div style='background-color:#FFF9C4; color:#F57F17; padding:10px; border-radius:5px; margin-bottom:8px; border-left:4px solid #FBC02D; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);'><b>⏳ {nome_fase}</b></div>", unsafe_allow_html=True)
                    else:
                        st.sidebar.markdown(f"<div style='background-color:#FFFFFF; color:#9E9E9E; padding:10px; border-radius:5px; margin-bottom:8px; border:1px solid #E0E0E0;'><b>🔒 {nome_fase}</b></div>", unsafe_allow_html=True)

                grafico = gerar_fluxograma_individual(etapa_destaque=id_etapa)
                st.graphviz_chart(grafico, use_container_width=False) 
            else:
                st.warning("Projeto não encontrado.")
                st.graphviz_chart(gerar_fluxograma_individual(), use_container_width=False)
    else:
        st.info(f"O módulo público para {tipo_contrato} estará disponível em breve.")

# ----------------- ABA CONFIDENCIAL (NAP) -----------------
with aba_nap:
    st.subheader("Painel de Gestão de Contratos")
    
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
            
        # --- O DROPDOWN DA VISÃO INTERNA ATUALIZADO ---
        st.markdown("---")
        tipo_contrato_nap = st.selectbox(
            "Selecione o Dashboard Gerencial que deseja visualizar:", 
            ["Acordos de Parceria", "Protocolo de Intenções (Em Breve)", "ACT (Em Breve)", "Contrato global (Em Breve)"],
            key="dropdown_interno"
        )
        
        if tipo_contrato_nap == "Acordos de Parceria":
            total_projetos = len(df[df['Registro'] != ''])
            st.write(f"Monitorando **{total_projetos}** projetos de Acordos de Parceria simultaneamente.")
            
            grafico_macro = gerar_fluxograma_geral(df)
            st.graphviz_chart(grafico_macro, use_container_width=False)
            
        else:
            st.info(f"🚧 O painel gerencial interno para {tipo_contrato_nap} está em desenvolvimento.")
