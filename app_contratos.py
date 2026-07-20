import streamlit as st
import pandas as pd
import graphviz
import textwrap

# Configuração da página e uso do tema nativo
st.set_page_config(layout="wide", page_title="Sistema Integra", page_icon="📊")

# ==========================================
# 1. CSS MODERNIZADO: PAINEL FIXO E FLUXOGRAMA
# ==========================================
st.markdown("""
    <style>
        /* Gráfico adaptável */
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
        
        /* Cabeçalho Fixo (Sticky) para Título e Progresso */
        .painel-fixo {
            position: sticky;
            top: 2.875rem; /* Altura padrão da barra superior do Streamlit */
            background-color: var(--secondary-background-color);
            z-index: 999;
            padding: 15px 20px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO COM O GOOGLE PLANILHAS
# ==========================================
# COLE O SEU LINK DO GOOGLE PLANILHAS AQUI DENTRO DAS ASPAS
url_google_sheets = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRXE69ipW9usXVW5msH5SPVV5CMz5tboAlWg_O-9Zdi4_WGxdB5BmTlXxdd_2OSrW6_S91J66bckSDs/pub?gid=409266791&single=true&output=csv"

try:
    # A MÁGICA ESTÁ AQUI: dtype=str impede que o Python engula os zeros à esquerda!
    df_bruto = pd.read_csv(url_google_sheets, dtype=str)
    
    # Limpa quebras de linha dos nomes das colunas
    df_bruto.columns = df_bruto.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
    
    df = df_bruto.rename(columns={
        'Registro Portal de Projetos': 'Registro',
        'Projeto/Título': 'Titulo',
        'Etapa Atual': 'Etapa_Atual' 
    })
    
    colunas_essenciais = ['Registro', 'Titulo', 'Etapa_Atual']
    faltaram = [col for col in colunas_essenciais if col not in df.columns]
    
    if faltaram:
        st.warning(f"⚠️ Atenção: As colunas não bateram. Lendo: {df_bruto.columns.tolist()}")
        for col in faltaram:
            df[col] = "" 
            
    # Força a ser string de novo, remove eventuais '.0' fantasmas e limpa espaços nas bordas
    df['Registro'] = df['Registro'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df['Titulo'] = df['Titulo'].astype(str).str.strip()
    df['Etapa_Atual'] = df['Etapa_Atual'].astype(str).str.replace('.0', '', regex=False).str.strip()

except Exception as e:
    st.error(f"Erro técnico ao ler a planilha: {e}")
    df = pd.DataFrame(columns=['Registro', 'Titulo', 'Etapa_Atual'])
# ==========================================
# 3. DICIONÁRIOS E MAPAS DE PROGRESSO
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

cores_caixas = {
    'Coordenador(a)': '#C8E6C9', 'NPV': '#FFF9C4', 'Juridico': '#FFCDD2',       
    'NPI': '#BBDEFB', 'NAP': '#E1BEE7', 'Outros': '#E0E0E0'          
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

# Função para classificar as Fases e o Progresso da Barra
def avaliar_status(id_etapa):
    if id_etapa in setores['Coordenador(a)']: return 20, 1
    elif id_etapa in setores['NPV']: return 40, 2
    elif id_etapa in setores['Juridico'] or id_etapa in setores['NPI']: return 60, 3
    elif id_etapa in setores['NAP'] or id_etapa in setores['Outros']: 
        if id_etapa in ['N_FIM', 'N_A_SEGUIR']: return 100, 5
        return 80, 4
    else: return 5, 1

# ==========================================
# 4. FUNÇÃO GERADORA DO FLUXOGRAMA VERTICAL
# ==========================================
def gerar_fluxograma(etapa_destaque=None):
    dot = graphviz.Digraph(comment='Fluxograma Completo')
    
    # rankdir='TB' para vertical. nodesep/ranksep controlam espaços.
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.6', ranksep='0.6')
    dot.attr('node', margin='0.1,0.05', width='0', height='0')
    
    for nome_setor, lista_ids in setores.items():
        cor_caixa = cores_caixas.get(nome_setor, '#FFFFFF')
        
        for id_caixa in lista_ids:
            texto_bruto = textos.get(id_caixa, id_caixa).replace('\n', ' ')
            linhas = textwrap.wrap(texto_bruto, width=22)
            texto_linhas = "\n".join(linhas)
            
            formato = 'box'
            if '?' in texto_bruto: formato = 'diamond'
            
            if id_caixa not in ['N_INICIO', 'N_FIM']:
                texto_exibicao = f"[{nome_setor.upper()}]\n{texto_linhas}"
            else:
                texto_exibicao = texto_linhas
            
            if id_caixa == 'N_INICIO':
                dot.node(id_caixa, texto_exibicao, shape='circle', style='filled', fillcolor='#4CAF50', color='#2E7D32', fontcolor='white', penwidth='3', fontname='Helvetica-Bold', fontsize='24')
            elif id_caixa == 'N_FIM':
                dot.node(id_caixa, texto_exibicao, shape='circle', style='filled', fillcolor='#F44336', color='#C62828', fontcolor='white', penwidth='3', fontname='Helvetica-Bold', fontsize='24')
            elif etapa_destaque and id_caixa == etapa_destaque:
                dot.node(id_caixa, texto_exibicao, shape=formato, style='filled, rounded', fillcolor='#FFD700', color='#B8860B', penwidth='4', fontname='Helvetica-Bold', fontsize='22')
            else:
                dot.node(id_caixa, texto_exibicao, shape=formato, style='filled, rounded', fillcolor=cor_caixa, color='#78909C', penwidth='2', fontname='Helvetica-Bold', fontsize='18')

    for conexao in conexoes:
        origem, destino = conexao[0], conexao[1]
        cor_seta = '#90A4AE'
        if len(conexao) == 3:
            dot.edge(origem, destino, label=f" {conexao[2]} ", fontsize='16', fontname='Helvetica-Bold', fontcolor='#1976D2', color=cor_seta, penwidth='2.0')
        else:
            dot.edge(origem, destino, color=cor_seta, penwidth='2.0')

    return dot

# ==========================================
# 5. ESTRUTURA DO APLICATIVO
# ==========================================
# Preparando abas para o futuro
aba_parcerias, aba_outros, aba_nap = st.tabs([
    "🤝 Acordos de Parceria", 
    "📝 Outros Contratos", 
    "⚙️ Visão Interna (NAP)"
])

# Construindo a visão atual dentro da Aba Principal
with aba_parcerias:
    st.title("Sistema Integra - Rastreamento de Parcerias")
    busca = st.text_input("Buscar Projeto (Ex: 066335 ou Nome do Projeto)")

    if busca:
        projeto = df[(df['Registro'].str.contains(busca, case=False, na=False)) | 
                     (df['Titulo'].str.contains(busca, case=False, na=False))]
                     
        if not projeto.empty:
            num_projeto = str(projeto.iloc[0]['Registro']).replace('.0', '')
            tit_projeto = str(projeto.iloc[0]['Titulo'])
            etapa_bruta = str(projeto.iloc[0]['Etapa_Atual']).strip().replace('.0', '')
            
            id_etapa = tradutor_etapas.get(etapa_bruta, etapa_bruta)
            nome_etapa = textos.get(id_etapa, etapa_bruta)
            
            porcentagem, etapa_macro = avaliar_status(id_etapa)
            
            # --- MARCA PÁGINAS LATERAL (SIDEBAR) ---
            fases_nomes = [
                "1. Submissão (Coordenador)",
                "2. Negociação (NPV)",
                "3. Análise (Jurídico/NPI)",
                "4. Enquadramento (NAP/PRA)",
                "5. Concluído"
            ]
            
            st.sidebar.markdown("### 📍 Linha do Tempo do Projeto")
            st.sidebar.markdown(f"**Projeto:** {num_projeto}")
            st.sidebar.markdown("---")
            
            for i, nome_fase in enumerate(fases_nomes, 1):
                if i < etapa_macro:
                    # Fase concluída (Fundo Verde)
                    st.sidebar.markdown(f"<div style='background-color:#E8F5E9; color:#2E7D32; padding:10px; border-radius:5px; margin-bottom:8px; border-left:4px solid #4CAF50;'><b>✅ {nome_fase}</b></div>", unsafe_allow_html=True)
                elif i == etapa_macro:
                    # Fase atual (Fundo Amarelo)
                    st.sidebar.markdown(f"<div style='background-color:#FFF9C4; color:#F57F17; padding:10px; border-radius:5px; margin-bottom:8px; border-left:4px solid #FBC02D; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);'><b>⏳ {nome_fase}</b></div>", unsafe_allow_html=True)
                else:
                    # Fase pendente (Fundo Branco)
                    st.sidebar.markdown(f"<div style='background-color:#FFFFFF; color:#9E9E9E; padding:10px; border-radius:5px; margin-bottom:8px; border:1px solid #E0E0E0;'><b>🔒 {nome_fase}</b></div>", unsafe_allow_html=True)

            # --- CABEÇALHO FIXO COM PORCENTAGEM (STICKY) ---
            st.markdown(f"""
                <div class="painel-fixo">
                    <h4 style="margin: 0 0 10px 0;">Nº {num_projeto} - {tit_projeto}</h4>
                    <div style="background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 20px;">
                        <div style="background-color: #4CAF50; width: {porcentagem}%; height: 100%; border-radius: 10px; transition: width 0.5s;"></div>
                    </div>
                    <p style="text-align: right; margin: 5px 0 0 0; font-size: 14px; font-weight: bold; color: var(--text-color);">
                        Status: {nome_etapa.replace(chr(10), ' ')} ({porcentagem}% concluído)
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- GERAR GRÁFICO ---
            grafico = gerar_fluxograma(etapa_destaque=id_etapa)
            st.graphviz_chart(grafico, use_container_width=False) 
        else:
            st.warning("Projeto não encontrado. Verifique se o nome ou número de registro estão corretos.")
            st.graphviz_chart(gerar_fluxograma(), use_container_width=False)
    else:
        st.info("Digite um número ou título acima para buscar e acompanhar o projeto.")
        st.graphviz_chart(gerar_fluxograma(), use_container_width=False)

# Deixando um esqueleto simples para as próximas telas
with aba_outros:
    st.write("Em breve: Fluxograma de outros tipos de contrato.")

with aba_nap:
    st.write("Em breve: Painel administrativo para acompanhamento geral do NAP.")
