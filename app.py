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
# 2. DESIGN PREMIUM E IDENTIDADE VISUAL
# ==========================================
st.set_page_config(page_title="Mais Embalagens - Gestão", page_icon="📦", layout="centered")

# Visual totalmente personalizado com as cores da logo 291246_2.png
st.markdown("""
    <style>
    /* Fundo principal azul escuro */
    .main { 
        background-color: #0B2545; 
        color: #FFFFFF; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Botão Salvar Vermelho Premium */
    .stButton>button { 
        background-color: #EE1D23; 
        color: white; 
        font-weight: bold; 
        font-size: 16px;
        width: 100%; 
        border-radius: 10px; 
        border: none;
        padding: 12px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #B31217; 
        color: white; 
        transform: scale(1.02);
    }
    
    /* Estilização das caixas de texto e seleção */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="popover"] {
        border-radius: 8px !important;
        background-color: #13315C !important;
        border: 1px solid #1D3D6B !important;
    }
    
    /* Cor dos textos das perguntas */
    label p {
        color: #F4D03F !important; /* Detalhes em Amarelo */
        font-weight: bold !important;
        font-size: 14px !important;
    }
    
    /* Ajustes das abas */
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        color: #F4D03F !important;
        border-bottom-color: #EE1D23 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Exibe a arte da empresa no topo se o arquivo estiver na pasta
try:
    st.image("291246_2.png", use_container_width=True)
except:
    st.title("MAIS EMBALAGENS +")
    st.subheader("Controle de Despesas")

st.markdown("---")

# Abas organizadas
aba_cadastro, aba_historico = st.tabs(["📝 Novo Lançamento Diário", "📊 Visão Mensal & Histórico"])

# ==========================================
# 3. ABA DE LANÇAMENTOS (Layout em cartões)
# ==========================================
with aba_cadastro:
    st.markdown("### 📥 Cadastrar Saída")
    
    # Data no padrão brasileiro de exibição e calendário começando na segunda-feira
    campo_data = st.date_input(
        "Data do Gasto:", 
        value=datetime.now(), 
        format="DD/MM/YYYY"
    )
    
    campo_desc = st.text_input("Descrição / Fornecedor / Destino:", placeholder="Ex: Compra de bobinas plásticas")
    
    # Categorias atualizadas com Deslocamento e Pessoal
    categorias_lista = ["Mercadoria", "Logística", "Deslocamento", "Pessoal", "Infraestrutura", "Funcionários", "Limpeza", "Outros"]
    campo_cat = st.selectbox("Categoria do Gasto:", categorias_lista)
    
    campo_valor = st.number_input("Valor total da Despesa (R$):", min_value=0.0, step=1.0, format="%.2f")

    st.write("") # Espaçamento
    if st.button("SALVAR NO BANCO DE DADOS"):
        if campo_desc and campo_valor > 0:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO despesas (data, descricao, categoria, valor) 
                VALUES (?, ?, ?, ?)
            """, (campo_data.strftime("%d/%m/%Y"), campo_desc, campo_cat, campo_valor))
            conexao.commit()
            st.success("Lançamento guardado com sucesso no banco de dados! 🎉")
        else:
            st.error("Por favor, preencha a descrição e certifique-se de que o valor é maior que zero.")

# ==========================================
# 4. ABA DE HISTÓRICO E VISÃO MENSAL PREMIUM
# ==========================================
with aba_historico:
    st.markdown("### 🔍 Histórico de Lançamentos")
    
    df = pd.read_sql_query("SELECT data as 'Data', descricao as 'Descrição', categoria as 'Categoria', valor as 'Valor (R$)' FROM despesas ORDER BY id DESC", conexao)
    
    if not df.empty:
        # Cria a visão mensal pegando o mês/ano da data
        df['Mês/Ano'] = df['Data'].str[3:] 
        meses_salvos = sorted(df['Mês/Ano'].unique(), reverse=True)
        
        filtro_mes = st.selectbox("Selecione o Mês para Análise:", ["Ver Todo o Histórico"] + list(meses_salvos))
        
        if filtro_mes != "Ver Todo o Histórico":
            df_filtrado = df[df['Mês/Ano'] == filtro_mes]
        else:
            df_filtrado = df

        total_gasto = df_filtrado['Valor (R$)'].sum()
        
        # Painel flutuante com o total acumulado do mês
        st.metric(
            label=f"Total Acumulado ({filtro_mes})", 
            value=f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        st.write("")
        # Mostra a tabela limpa
        st.dataframe(df_filtrado.drop(columns=['Mês/Ano']), use_container_width=True)
    else:
        st.info("O banco de dados ainda está vazio. Faça o seu primeiro lançamento na aba ao lado!")
