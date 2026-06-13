import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONEXÃO COM O BANCO DE DADOS (SQLite)
# ==========================================
def conectar_banco():
    # Cria ou conecta ao arquivo de banco de dados da Mais Embalagens
    conexao = sqlite3.connect("mais_embalagens_dados.db")
    cursor = conexao.cursor()
    # Cria a tabela de despesas se ela ainda não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            categoria TEXT,
            valor REAL
        )
    """)
    conexao.commit()
    return conexao

# Inicializa a ligação ao banco de dados
conexao = conectar_banco()

# ==========================================
# 2. DESIGN DA INTERFACE (Cores da sua Logo)
# ==========================================
# Configuração visual para telemóvel
st.set_page_config(page_title="Mais Embalagens", page_icon="📦", layout="centered")

# Cores da Logo: Azul Escuro (#0B2545), Vermelho (#EE1D23), Amarelo (#F4D03F)
st.markdown("""
    <style>
    .main { background-color: #0B2545; color: white; }
    .stButton>button { background-color: #EE1D23; color: white; font-weight: bold; width: 100%; border-radius: 8px; }
    .stButton>button:hover { background-color: #B31217; color: white; }
    h1, h2, h3 { color: white !important; }
    div[data-baseweb="select"] { background-color: #13315C; }
    </style>
""", unsafe_allow_html=True)

# Título do Sistema
st.title("MAIS EMBALAGENS +")
st.subheader("Gestão Profissional de Despesas")

# Abas para organizar o ecrã do telemóvel
aba_cadastro, aba_historico = st.tabs(["📝 Lançamento Diário", "📊 Visão Mensal & Histórico"])

# ==========================================
# 3. ABA DE LANÇAMENTOS
# ==========================================
with aba_cadastro:
    st.write("### Novo Gasto")
    
    # Campos fáceis de tocar no telemóvel
    campo_data = st.date_input("Data do Lançamento:", datetime.now())
    campo_desc = st.text_input("Descrição / Fornecedor:")
    campo_cat = st.selectbox("Categoria:", ["Mercadoria", "Logística", "Infraestrutura", "Funcionários", "Limpeza", "Outros"])
    campo_valor = st.number_input("Valor da Despesa (R$):", min_value=0.0, step=1.0, format="%.2f")

    if st.button("SALVAR NO BANCO DE DADOS"):
        if campo_desc and campo_valor > 0:
            cursor = conexao.cursor()
            # Comando SQL para inserir os dados que digitou no banco de dados
            cursor.execute("""
                INSERT INTO despesas (data, descricao, categoria, valor) 
                VALUES (?, ?, ?, ?)
            """, (campo_data.strftime("%d/%m/%Y"), campo_desc, campo_cat, campo_valor))
            conexao.commit()
            st.success("Lançamento guardado com sucesso! 🎉")
        else:
            st.error("Por favor, preencha a descrição e o valor.")

# ==========================================
# 4. ABA DE HISTÓRICO E VISÃO MENSAL
# ==========================================
with aba_historico:
    st.write("### Histórico e Filtros")
    
    # Lendo os dados do SQLite usando o Pandas (Biblioteca de Relatórios)
    df = pd.read_sql_query("SELECT data as 'Data', descricao as 'Descrição', categoria as 'Categoria', valor as 'Valor (R$)' FROM despesas ORDER BY id DESC", conexao)
    
    if not df.empty:
        # Cria a visão mensal pegando o mês/ano da data
        df['Mês/Ano'] = df['Data'].str[3:] 
        meses_salvos = df['Mês/Ano'].unique()
        
        # Filtro na tela
        filtro_mes = st.selectbox("Escolha o Mês para Análise:", ["Ver Tudo"] + list(meses_salvos))
        
        if filtro_mes != "Ver Tudo":
            df_filtrado = df[df['Mês/Ano'] == filtro_mes]
        else:
            df_filtrado = df

        # Calcula o total acumulado do mês selecionado
        total_gasto = df_filtrado['Valor (R$)'].sum()
        
        # Exibe o painel de valor grande e profissional
        st.metric(label=f"Total de Despesas ({filtro_mes})", value=f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        # Mostra a tabela organizada
        st.dataframe(df_filtrado.drop(columns=['Mês/Ano']), use_container_width=True)
    else:
        st.info("O banco de dados ainda está vazio. Faça o seu primeiro lançamento!")

