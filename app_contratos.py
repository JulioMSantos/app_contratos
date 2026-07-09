import streamlit as st
import pandas as pd
import graphviz

# 1. Simulando a sua planilha de controle (no futuro, você substitui por pd.read_excel('sua_planilha.xlsx'))
dados = {
    'Registro': ['PRJ-001', 'PRJ-002', 'PRJ-003'],
    'Titulo': ['Desenvolvimento Sensor de Gás Automatizado', 'Parceria Petrobras e CMPC', 'Plano de Trabalho Fundep'],
    'Etapa_Atual': ['NPI', 'Formalização', 'Coordenador(a)']
}
df = pd.DataFrame(dados)

# Definindo a ordem oficial das etapas do seu PDF
ordem_etapas = [
    'Outros', 'NAP', 'NPV', 'Coordenador(a)', 
    'Juridico', 'NPI', 'Formalização', 'Vigência', 'Pós-Vigência'
]

# 2. Interface do Streamlit
st.title("Rastreamento de Etapas de Contratos")
st.write("Digite o registro ou título do projeto para visualizar o status.")

# Barra de busca
busca = st.text_input("Buscar Projeto (Ex: PRJ-001 ou Sensor de Gás)")

if busca:
    # Filtra a planilha com base na busca
    projeto_encontrado = df[(df['Registro'].str.contains(busca, case=False)) | 
                            (df['Titulo'].str.contains(busca, case=False))]
    
    if not projeto_encontrado.empty:
        # Pega as informações do projeto
        titulo = projeto_encontrado.iloc[0]['Titulo']
        etapa_atual = projeto_encontrado.iloc[0]['Etapa_Atual']
        
        st.subheader(f"Projeto: {titulo}")
        st.write(f"**Etapa Atual:** {etapa_atual}")
        
        # 3. Construindo o Fluxograma Visual
        dot = graphviz.Digraph(comment='Fluxograma do Contrato')
        dot.attr(rankdir='LR') # LR = Left to Right (Esquerda para Direita). Use 'TB' para Top to Bottom.
        
        # Descobre o índice (número) da etapa atual para saber o que já passou e o que falta
        try:
            indice_atual = ordem_etapas.index(etapa_atual)
        except ValueError:
            indice_atual = -1
            
        # Criando as caixas do fluxograma dinamicamente
        for i, etapa in enumerate(ordem_etapas):
            if i < indice_atual:
                # Etapas já concluídas: cinza claro
                dot.node(etapa, etapa, style='filled', fillcolor='#E0E0E0', shape='box', color='gray')
            elif i == indice_atual:
                # Etapa atual: destacada em amarelo/laranja
                dot.node(etapa, etapa, style='filled', fillcolor='#FFD700', shape='box', penwidth='2')
            else:
                # Etapas futuras: branco com borda tracejada
                dot.node(etapa, etapa, style='dashed', shape='box', color='#888888')
                
            # Conectando as setas (da etapa atual para a próxima)
            if i > 0:
                dot.edge(ordem_etapas[i-1], etapa)

        # Renderiza o fluxograma na tela
        st.graphviz_chart(dot)
        
    else:
        st.warning("Projeto não encontrado. Verifique o termo buscado.")