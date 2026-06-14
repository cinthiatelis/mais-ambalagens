import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONEXÃO COM O BANCO DE DADOS
# ==========================================
def conectar_banco():
    conexao = sqlite3.connect("mais_embalagens_dados.db")
    cursor = conexao.cursor()
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

conexao = conectar_banco()

# ==========================================
# 2. DESIGN PREMIUM - LEITURA GARANTIDA
# ==========================================
st.set_page_config(page_title="Mais Embalagens - Gestão", page_icon="📦", layout="centered")

st.markdown("""
    <style>
    /* Fundo principal claro */
    .stApp, .main, [data-testid="stAppViewContainer"] { 
        background-color: #FFFFFF !important; 
        color: #1E293B !important; 
    }
    
    /* Força todos os textos normais e parágrafos a ficarem escuros */
    p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #1E293B !important;
    }
    
    /* BOTÃO SALVAR VERMELHO PREMIUM */
    .stButton>button { 
        background-color: #EE1D23 !important; 
        color: white !important; 
        font-weight: bold !important; 
        font-size: 16px !important;
        width: 100% !important; 
        border-radius: 10px !important; 
        border: none !important;
        padding: 12px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    .stButton>button p {
        color: white !important;
    }
    
    /* CORREÇÃO DO MENU E CAIXAS DE SELEÇÃO (Contraste Máximo) */
    /* Deixa as caixas de texto e o menu que desce escuros, mas força as letras a ficarem brancas */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="popover"], ul, li {
        background-color: #1E293B !important;
        border-radius: 8px !important;
    }
    
    /* Força a cor branca em TODAS as letras dentro das caixas e listas de seleção */
    input, select, div[data-baseweb="select"] *, ul *, li * {
        color: #FFFFFF !important;
    }
    
    /* Títulos dos campos acima das caixas (Em Azul Escuro) */
    label p {
        color: #0B2545 !important; 
        font-weight: bold !important;
        font-size: 15px !important;
    }
    
    /* Customização das Abas */
    .stTabs [data-baseweb="tab"] p {
        color: #64748B !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #0B2545 !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #EE1D23 !important;
    }
    
    /* Tabelas com fundo claro */
    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Exibe a logo da empresa no topo
try:
    st.image("304484.png", use_container_width=True)
except:
    st.markdown("<h1 style='color: #0B2545; text-align: center; font-family: Arial;'>MAIS EMBALAGENS +</h1>", unsafe_allow_html=True)

st.markdown("---")

# Abas organizadas
aba_cadastro, aba_historico = st.tabs(["📝 Novo Lançamento Diário", "📊 Visão Mensal & Histórico"])

# ==========================================
# 3. ABA DE LANÇAMENTOS
# ==========================================
with aba_cadastro:
    st.markdown("<h3 style='color: #0B2545; font-family: Arial;'>📥 Cadastrar Saída</h3>", unsafe_allow_html=True)
    
    campo_data = st.date_input(
        "Data do Gasto:", 
        value=datetime.now(), 
        format="DD/MM/YYYY"
    )
    
    campo_desc = st.text_input("Descrição / Fornecedor / Destino:", placeholder="Ex: Compra de bobinas plásticas")
    
    categorias_lista = ["Mercadoria", "Logística", "Deslocamento", "Pessoal", "Infraestrutura", "Funcionários", "Limpeza", "Outros"]
    campo_cat = st.selectbox("Categoria do Gasto:", categorias_lista)
    
    campo_valor = st.number_input("Valor total da Despesa (R$):", min_value=0.0, step=1.0, format="%.2f")

    st.write("") 
    if st.button("SALVAR NO BANCO DE DADOS"):
        if campo_desc and campo_valor > 0:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO despesas (data, descricao, categoria, valor) 
                VALUES (?, ?, ?, ?)
            """, (campo_data.strftime("%d/%m/%Y"), campo_desc, campo_cat, campo_valor))
            conexao.commit()
            st.success("Lançamento guardado com sucesso! 🎉")
        else:
            st.error("Por favor, preencha a descrição e o valor corretamente.")

# ==========================================
# 4. ABA DE HISTÓRICO E VISÃO MENSAL
# ==========================================
with aba_historico:
    st.markdown("<h3 style='color: #0B2545; font-family: Arial;'>🔍 Histórico de Lançamentos</h3>", unsafe_allow_html=True)
    
    df = pd.read_sql_query("SELECT data as 'Data', descricao as 'Descrição', categoria as 'Categoria', valor as 'Valor (R$)' FROM despesas ORDER BY id DESC", conexao)
    
    if not df.empty:
        df['Mês/Ano'] = df['Data'].str[3:] 
        meses_salvos = sorted(df['Mês/Ano'].unique(), reverse=True)
        
        filtro_mes = st.selectbox("Selecione o Mês para Análise:", ["Ver Todo o Histórico"] + list(meses_salvos))
        
        if filtro_mes != "Ver Todo o Histórico":
            df_filtrado = df[df['Mês/Ano'] == filtro_mes]
        else:
            df_filtrado = df

        total_gasto = df_filtrado['Valor (R$)'].sum()
        
        st.metric(
            label=f"Total Acumulado ({filtro_mes})", 
            value=f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        st.write("")
        st.dataframe(df_filtrado.drop(columns=['Mês/Ano']), use_container_width=True)
    else:
        st.info("O banco de dados está vazio. Comece a lançar para ver o histórico!")
