import streamlit as st
import pandas as pd
import graphviz

st.set_page_config(layout="wide")

# 1. Base de Dados
dados = {
    'Registro': ['PRJ-001', 'PRJ-002', 'PRJ-003'],
    'Titulo': ['Sensor de Gás', 'Parceria Petrobras', 'Acordo CMPC'],
    'Etapa_Atual': ['N_J20_2_1', 'N_PI18_2_1', 'N_A15_1'] 
    # Agora a planilha usa o ID da etapa (veja o dicionario abaixo)
}
df = pd.DataFrame(dados)

# 2. Dicionário de Textos (ID -> Texto que aparece na tela)
# Os \n servem para quebrar a linha e a caixa não ficar larga demais
textos = {
    # COORDENADOR
    'N_INICIO': 'Início',
    'N_C1': '1. Abrir processo no PEN\ne preencher formulário',
    'N_C_D1': 'Algum documento\npreviamente acordado?',
    'N_C2': '2. Anexar ao Processo PEN',
    'N_C3': '3. Tramitar para o NPV',
    'N_C6': '6. Elaborar a proposta\ninicial para a Empresa',
    'N_C13': '13. Responder o e-mail',
    'N_C15_3': '15.3 Enviar documentação\npreenchida',
    'N_C17_2_1': '17.2.1 Preencher declaração\ne enviar ao NPI',
    
    # NPV
    'N_V4': '4. Realizar reunião de\ncomunicação do projeto',
    'N_V5': '5. Enviar material\ninformativo',
    'N_V_D1': 'Precisa determinar a\ndivisão de PI?',
    'N_V_D2': 'Precisa valorar?',
    'N_V10_2_2': '10.2.2 Valoração',
    'N_V_SEGUIR': 'Seguir independentemente',
    'N_V_D3': 'Negociação pela NPV?',
    'N_V10': '10. Negociar e fechar\na proposta',
    'N_V11': '11. Tramitar para o NAP',
    'N_V7': '7. Analisar e Tramitar\npara o NAP',
    'N_V12': '12. Enviar modelo de e-mail\n"Escolha Fundação"',
    'N_V14_1': '14.1 Enviar a documentação\npara instrução processual',
    'N_V14_2': '14.2 Encaminhar a demanda\nao jurídico por e-mail',
    'N_V_D4': 'Qual o tipo de\nnegociação de TT?',
    'N_V16_2_3': '16.2.3 Negociar as\ncláusulas do contrato',
    'N_V20_2_2': '20.2.2 Emitir relatório\nde negociação',
    'N_V16_2_2': '16.2.2 Valoração',
    'N_V17_2_2': '17.2.2 Emitir relatório\ntécnico de valoração',
    'N_V18_2_2': '18.2.2 Emitir parecer\nde valoração',
    'N_V19_2_2': '19.2.2 Enviar para\no Jurídico',
    
    # NAP
    'N_A8': '8. Analisar e\nEnquadramento',
    'N_A_D1': 'É um Acordo de parceria?',
    'N_A_SEGUIR': 'Seguir conforme o\nenquadramento',
    'N_FIM': 'FIM',
    'N_A9': '9. Tramitar para o NPV',
    'N_A15_1': '15.1 Analisar a\ndocumentação',
    'N_A17_3': '17.3 Encaminhar por e-mail\npara análise da PRA',
    'N_A_D2': 'Documentação precisa\nde correção?',
    'N_A20_3': '20.3 Retornar por e-mail\nao coordenador',
    'N_A20_1': '20.1 Anexar documentos\ne solicitar Fundação',
    'N_A22_1': '22.1 Coletar assinaturas',
    'N_A23_1': '23.1 Tramitar para a PRA',
    
    # JURÍDICO
    'N_J_D1': 'Empresa tem\nprópria minuta?',
    'N_J15_2_1': '15.2.1 Analisar minuta\nencaminhada',
    'N_J15_2_2': '15.2.2 Encaminhar minuta\npadrão AGU',
    'N_J_D2': '16.2.1 Tem questões de\ndivisão de PI?',
    'N_J_D3': 'Tem questões para\nnegociar de TT?',
    'N_J20_2_1': '20.2.1 Elaborar a minuta',
    'N_J21_2': '21.2 Fechar a minuta',
    'N_J_D4': 'Precisa quadro comparativo?',
    
    # NPI
    'N_PI16_2_1': '16.2.1 Encaminhar e-mail\ndeclaração de atividades',
    'N_PI18_2_1': '18.2.1 Definir percentual de PI\ne emitir parecer',
    'N_PI19_2_1': '19.2.1 Encaminhar e-mail\npara Empresa, Coord e Jurídico',
    
    # OUTROS (PRA)
    'N_O18_1': '18.1 Analisar a\ndocumentação (PRA)',
    'N_O19_1': '19.1 Enviar por e-mail\npara o NAP (PRA)',
    'N_O24': '24. Realizar análise (PRA)',
    'N_O25': '25. Emitir parecer (PRA)',
    'N_O26': '26. Inserir CADIN (PRA)',
    'N_O27': '27. Tramitar ao NAP (PRA)'
}

# 3. Distribuição das Etapas por Setor
setores = {
    'NPI': ['N_PI16_2_1', 'N_PI18_2_1', 'N_PI19_2_1'],
    'Juridico': ['N_J_D1', 'N_J15_2_1', 'N_J15_2_2', 'N_J_D2', 'N_J_D3', 'N_J20_2_1', 'N_J21_2', 'N_J_D4'],
    'Coordenador(a)': ['N_INICIO', 'N_C1', 'N_C_D1', 'N_C2', 'N_C3', 'N_C6', 'N_C13', 'N_C15_3', 'N_C17_2_1'],
    'NPV': ['N_V4', 'N_V5', 'N_V_D1', 'N_V_D2', 'N_V10_2_2', 'N_V_SEGUIR', 'N_V_D3', 'N_V10', 'N_V11', 'N_V7', 'N_V12', 'N_V14_1', 'N_V14_2', 'N_V_D4', 'N_V16_2_3', 'N_V20_2_2', 'N_V16_2_2', 'N_V17_2_2', 'N_V18_2_2', 'N_V19_2_2'],
    'NAP': ['N_A8', 'N_A_D1', 'N_A_SEGUIR', 'N_FIM', 'N_A9', 'N_A15_1', 'N_A17_3', 'N_A_D2', 'N_A20_3', 'N_A20_1', 'N_A22_1', 'N_A23_1'],
    'Outros': ['N_O18_1', 'N_O19_1', 'N_O24', 'N_O25', 'N_O26', 'N_O27']
}

# 4. Mapeamento das Setas Exatas (De onde -> Para onde)
conexoes = [
    # Início do Fluxo
    ('N_INICIO', 'N_C1'), ('N_C1', 'N_C_D1'),
    ('N_C_D1', 'N_C2', 'Sim'), ('N_C_D1', 'N_C3', 'Não'),
    ('N_C2', 'N_C3'), ('N_C3', 'N_V4'), ('N_V4', 'N_V5'),
    ('N_V5', 'N_V_D1'),
    
    # Decisão PI (NPV para Coord)
    ('N_V_D1', 'N_C6', 'Sim'), ('N_C6', 'N_V7'),
    
    # Caminho Negociação (NPV)
    ('N_V_D1', 'N_V_D2', 'Não'),
    ('N_V_D2', 'N_V10_2_2', 'Sim'), ('N_V_D2', 'N_V_SEGUIR', 'Não'),
    ('N_V10_2_2', 'N_V_D3'), ('N_V_SEGUIR', 'N_V_D3'),
    ('N_V_D3', 'N_V10', 'Sim'), ('N_V10', 'N_V11'),
    ('N_V_D3', 'N_V7', 'Não'), ('N_V11', 'N_A8'), ('N_V7', 'N_A8'),
    
    # Caminho NAP (Enquadramento)
    ('N_A8', 'N_A_D1'), ('N_A_D1', 'N_A_SEGUIR', 'Não'), ('N_A_SEGUIR', 'N_FIM'),
    ('N_A_D1', 'N_A9', 'Sim'), ('N_A9', 'N_V12'), ('N_V12', 'N_C13'),
    ('N_C13', 'N_V14_1'), ('N_V14_1', 'N_C15_3'), ('N_C15_3', 'N_V14_2'),
    
    # Bifurcação Jurídico e NAP
    ('N_V14_2', 'N_J_D1'), ('N_V14_2', 'N_A15_1'),
    
    # ------------------ RAMO JURÍDICO E NPI ------------------
    ('N_J_D1', 'N_J15_2_1', 'Sim'), ('N_J_D1', 'N_J15_2_2', 'Não'),
    ('N_J15_2_1', 'N_J_D2'), ('N_J15_2_2', 'N_J_D2'),
    
    # Divisão de PI (NPI)
    ('N_J_D2', 'N_PI16_2_1', 'Sim'),
    ('N_PI16_2_1', 'N_C17_2_1'), ('N_C17_2_1', 'N_PI18_2_1'), 
    ('N_PI18_2_1', 'N_PI19_2_1'), ('N_PI19_2_1', 'N_J20_2_1'),
    
    # Questões de TT
    ('N_J_D2', 'N_J_D3', 'Não'),
    ('N_J_D3', 'N_J20_2_1', 'Não'), ('N_J_D3', 'N_V_D4', 'Sim'),
    
    ('N_V_D4', 'N_V16_2_3', 'Diferentes'), ('N_V16_2_3', 'N_V20_2_2'), ('N_V20_2_2', 'N_J20_2_1'),
    ('N_V_D4', 'N_V16_2_2', 'Valoração'), ('N_V16_2_2', 'N_V17_2_2'), ('N_V17_2_2', 'N_V18_2_2'), 
    ('N_V18_2_2', 'N_V19_2_2'), ('N_V19_2_2', 'N_J20_2_1'),
    
    ('N_J20_2_1', 'N_J21_2'), ('N_J21_2', 'N_J_D4'),
    
    # ------------------ RAMO NAP E OUTROS ------------------
    ('N_A15_1', 'N_A17_3'), ('N_A17_3', 'N_O18_1'), ('N_O18_1', 'N_O19_1'),
    ('N_O19_1', 'N_A_D2'),
    ('N_A_D2', 'N_A20_3', 'Sim'), ('N_A20_3', 'N_C15_3'),
    ('N_A_D2', 'N_A20_1', 'Não'), ('N_A20_1', 'N_A22_1'), ('N_A22_1', 'N_A23_1'),
    ('N_A23_1', 'N_O24'), ('N_O24', 'N_O25'), ('N_O25', 'N_O26'), ('N_O26', 'N_O27')
]


def gerar_fluxograma(etapa_destaque=None):
    dot = graphviz.Digraph(comment='Fluxograma Completo')
    # Configurações para lidar com um gráfico gigante (nodesep e ranksep espaçam as caixas)
    dot.attr(rankdir='LR', compound='true', splines='ortho', nodesep='0.5', ranksep='0.7')
    
    for nome_setor, lista_ids in setores.items():
        with dot.subgraph(name=f'cluster_{nome_setor}') as c:
            c.attr(label=nome_setor, style='filled', color='#F4F6F9', fontname='Helvetica-Bold', fontsize='14', labelloc='t', labeljust='l', margin='20')
            
            for id_caixa in lista_ids:
                texto_real = textos.get(id_caixa, id_caixa)
                
                # Regras de Formato (Losango para perguntas)
                formato = 'box'
                if '?' in texto_real:
                    formato = 'diamond'
                elif texto_real in ['Início', 'FIM']:
                    formato = 'circle'
                
                # Regras de Destaque
                if etapa_destaque and id_caixa == etapa_destaque:
                    # Projeto atual = Amarelo Destaque
                    c.node(id_caixa, texto_real, shape=formato, style='filled', fillcolor='#FFD700', penwidth='3', fontname='Helvetica-Bold')
                else:
                    # Resto = Branco padrão
                    c.node(id_caixa, texto_real, shape=formato, style='filled', fillcolor='white', fontname='Helvetica', fontsize='16')

    # Traça as setas
    for conexao in conexoes:
        origem = conexao[0]
        destino = conexao[1]
        
        if len(conexao) == 3:
            dot.edge(origem, destino, label=conexao[2], fontsize='9', fontname='Helvetica-Bold', fontcolor='#0055A4', color='#666666')
        else:
            dot.edge(origem, destino, color='#666666')

    return dot

# 5. Interface Streamlit
st.title("Sistema Integra - Rastreamento de Contratos")
busca = st.text_input("Buscar Projeto (Ex: PRJ-001)")

if busca:
    projeto = df[df['Registro'].str.contains(busca, case=False)]
    if not projeto.empty:
        id_etapa = projeto.iloc[0]['Etapa_Atual']
        nome_etapa = textos.get(id_etapa, "Desconhecida")
        st.success(f"**Projeto Encontrado! Etapa Atual:** {nome_etapa}")
        
        grafico = gerar_fluxograma(etapa_destaque=id_etapa)
        # O False permite que você dê scroll horizontal no gráfico enorme sem ele ficar espremido
        st.graphviz_chart(grafico, use_container_width=False) 
    else:
        st.warning("Projeto não encontrado.")
        st.graphviz_chart(gerar_fluxograma(), use_container_width=False)
else:
    st.graphviz_chart(gerar_fluxograma(), use_container_width=False)
