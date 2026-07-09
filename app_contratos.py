import streamlit as st
import pandas as pd
import graphviz

# Configura a página para ficar mais larga (ideal para fluxogramas grandes)
st.set_page_config(layout="wide")

# 1. Base de Dados Simulada
dados = {
    'Registro': ['PRJ-001', 'PRJ-002', 'PRJ-003'],
    'Titulo': ['Desenvolvimento Sensor de Gás', 'Parceria Petrobras', 'Plano de Trabalho'],
    'Etapa_Atual': ['Valoração NPV', 'Análise Jurídica', 'Abertura de Processo']
}
df = pd.DataFrame(dados)

# 2. Mapeamento das Etapas e Setores
# Aqui nós definimos quais caixas pertencem a quais raias (departamentos)
setores = {
    'NPI': ['Análise de PI'],
    'Jurídico': ['Análise Jurídica', 'Assinatura do Contrato'],
    'Coordenador(a)': ['Abertura de Processo', 'Ajustes da Proposta'],
    'NPV': ['Valoração NPV', 'Negociação'],
    'NAP': ['Análise NAP', 'Tramitação Final'],
    'Outros': ['Fim']
}

# Ordem cronológica lógica para calcular o que é passado, presente e futuro
ordem_cronologica = [
    'Abertura de Processo', 'Análise NAP', 'Valoração NPV', 
    'Negociação', 'Análise de PI', 'Análise Jurídica', 
    'Ajustes da Proposta', 'Assinatura do Contrato', 'Tramitação Final', 'Fim'
]

# 3. Função para desenhar o fluxograma
def gerar_fluxograma(etapa_destaque=None):
    dot = graphviz.Digraph(comment='Fluxograma com Raias')
    dot.attr(rankdir='LR', compound='true', splines='ortho') # 'ortho' deixa as linhas retas
    
    # Descobre o índice da etapa atual para a lógica de cores
    indice_atual = -1
    if etapa_destaque and etapa_destaque in ordem_cronologica:
        indice_atual = ordem_cronologica.index(etapa_destaque)

    # Criação das Raias (Clusters)
    for nome_setor, etapas_do_setor in setores.items():
        # O nome do cluster no graphviz PRECISA começar com "cluster_"
        with dot.subgraph(name=f'cluster_{nome_setor}') as c:
            c.attr(label=nome_setor, style='filled', color='#f4f4f8', fontname='Helvetica', fontsize='14')
            
            for etapa in etapas_do_setor:
                indice_etapa = ordem_cronologica.index(etapa) if etapa in ordem_cronologica else 999
                
                if etapa_destaque:
                    # Lógica de Cores quando um projeto é pesquisado
                    if indice_etapa < indice_atual:
                        c.node(etapa, etapa, style='filled', fillcolor='#D3D3D3', color='gray', shape='box') # Concluído (Cinza)
                    elif indice_etapa == indice_atual:
                        c.node(etapa, etapa, style='filled', fillcolor='#FFD700', shape='box', penwidth='2') # Atual (Amarelo)
                    else:
                        c.node(etapa, etapa, style='dashed', fillcolor='white', color='gray', shape='box') # Futuro (Tracejado)
                else:
                    # Lógica de Cores Padrão (Sem pesquisa)
                    c.node(etapa, etapa, style='filled', fillcolor='white', shape='box')

    # Conectando as setas (fazendo o caminho do fluxograma cruzar os setores)
    for i in range(len(ordem_cronologica) - 1):
        dot.edge(ordem_cronologica[i], ordem_cronologica[i+1])

    return dot

# 4. Interface do Streamlit
st.title("Rastreamento de Etapas de Contratos")
st.write("Visão geral do processo. Pesquise um projeto para destacar o seu andamento.")

busca = st.text_input("Buscar Projeto (Ex: PRJ-001 ou Sensor de Gás)")

# Lógica de exibição
if busca:
    projeto_encontrado = df[(df['Registro'].str.contains(busca, case=False)) | 
                            (df['Titulo'].str.contains(busca, case=False))]
    
    if not projeto_encontrado.empty:
        titulo = projeto_encontrado.iloc[0]['Titulo']
        etapa_atual = projeto_encontrado.iloc[0]['Etapa_Atual']
        
        st.success(f"**Projeto Encontrado:** {titulo} | **Etapa Atual:** {etapa_atual}")
        
        # Gera o gráfico com o destaque
        grafico = gerar_fluxograma(etapa_destaque=etapa_atual)
        st.graphviz_chart(grafico, use_container_width=True)
    else:
        st.warning("Projeto não encontrado. Mostrando fluxograma padrão.")
        grafico = gerar_fluxograma()
        st.graphviz_chart(grafico, use_container_width=True)
else:
    # Se a barra de busca estiver vazia, exibe o fluxograma limpo
    grafico = gerar_fluxograma()
    st.graphviz_chart(grafico, use_container_width=True)
