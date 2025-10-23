# CÉLULA %%writefile app.py (VERSÃO MULTI-ANO COM FILTRO DE ANO)

%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Análise de Dengue no Brasil (Multi-Ano)", page_icon="🦟", layout="wide")

# --- ESTILO CSS ---
st.markdown("""<style> [data-testid="stSidebar"] { background-color: #ADD8E6; } footer {visibility: hidden;} </style>""", unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO (Lê o CSV multi-ano salvo localmente) ---
@st.cache_data
def carregar_dados_locais():
    try:
        caminho_local_csv = '/content/dados_limpos_para_app.csv'
        df = pd.read_csv(caminho_local_csv, sep=',', encoding='latin-1')
        # Prepara colunas de mapeamento
        mapa_uf = { 11:'RO', 12:'AC', 13:'AM', 14:'RR', 15:'PA', 16:'AP', 17:'TO', 21:'MA', 22:'PI', 23:'CE', 24:'RN', 25:'PB', 26:'PE', 27:'AL', 28:'SE', 29:'BA', 31:'MG', 32:'ES', 33:'RJ', 35:'SP', 41:'PR', 42:'SC', 43:'RS', 50:'MS', 51:'MT', 52:'GO', 53:'DF' }
        df['ESTADO'] = df['SG_UF_NOT'].map(mapa_uf)
        mapa_sexo = {'M': 'Masculino', 'F': 'Feminino', 'I': 'Ignorado'}
        df['SEXO'] = df['CS_SEXO'].map(mapa_sexo)
        mapa_criterio = {1.0: 'Laboratorial', 2.0: 'Clínico-Epidem.', 3.0: 'Em Investigação'}
        df['CRITERIO_DESC'] = df['CRITERIO'].map(mapa_criterio)
        # Garante que colunas importantes não tenham NaNs e que NU_ANO seja inteiro
        df.dropna(subset=['ESTADO', 'NU_ANO'], inplace=True)
        df['NU_ANO'] = df['NU_ANO'].astype(int)
        return df
    except FileNotFoundError:
        st.error("ERRO: O arquivo 'dados_limpos_para_app.csv' não foi encontrado.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar/processar dados locais: {e}")
        return None

# --- CARREGA OS DADOS ---
df_analise = carregar_dados_locais()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("Filtros")
try:
    st.sidebar.image("https://logodownload.org/wp-content/uploads/2014/02/sus-logo-0.png", width=100)
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Flag_of_Brazil.svg/200px-Flag_of_Brazil.svg.png", width=100)
except Exception:
    pass

if df_analise is not None:
    anos_disponiveis = sorted(df_analise['NU_ANO'].unique())
    # === ADIÇÃO DO FILTRO DE ANO ===
    anos_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Ano(s):",
        options=anos_disponiveis,
        default=anos_disponiveis # Começa com todos os anos selecionados
    )
    # ================================

    lista_estados = sorted(df_analise['ESTADO'].unique())
    estados_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Estado(s) (Opcional):",
        options=lista_estados,
        default=[]
    )

    # Aplica os filtros de ANO e ESTADO
    if not anos_selecionados: # Garante que pelo menos um ano esteja selecionado
        anos_selecionados = anos_disponiveis
    # Filtra primeiro por ANO
    df_filtrado = df_analise[df_analise['NU_ANO'].isin(anos_selecionados)]

    # Depois filtra por ESTADO (se algum foi selecionado)
    if estados_selecionados:
        df_filtrado = df_filtrado[df_filtrado['ESTADO'].isin(estados_selecionados)]
        titulo_local = f"{', '.join(estados_selecionados)}"
    else:
        titulo_local = "Brasil"

    titulo_anos = f"({min(anos_selecionados)}-{max(anos_selecionados)})" if len(anos_selecionados) > 1 else f"({anos_selecionados[0]})"
    titulo_principal = f"Análise de Dengue - {titulo_local} {titulo_anos}"

else:
    df_filtrado = pd.DataFrame()
    titulo_principal = "Análise de Dengue - Erro ao carregar dados"
    st.sidebar.error("Dados não carregados, filtros desativados.")

# --- INTERFACE PRINCIPAL DA APLICAÇÃO ---
st.title(f"🦟 {titulo_principal}")
st.markdown("Análise interativa dos dados de notificação de Dengue do SINAN.")

if not df_filtrado.empty:
    # Gráfico 1: Evolução Temporal
    st.header("Evolução Anual dos Casos (Seleção Atual)")
    casos_por_ano_filtrado = df_filtrado['NU_ANO'].value_counts().sort_index().reset_index()
    casos_por_ano_filtrado.columns = ['Ano', 'Numero_de_Casos']
    fig_linha = px.line(casos_por_ano_filtrado, x='Ano', y='Numero_de_Casos', title='Casos Notificados por Ano', markers=True)
    st.plotly_chart(fig_linha, use_container_width=True)

    # Gráfico 2: Distribuição por Estado
    st.header("Distribuição por Estado (Seleção Atual)")
    casos_estado_filtrado = df_filtrado['ESTADO'].value_counts().reset_index()
    casos_estado_filtrado.columns = ['Estado', 'Numero_de_Casos']
    fig_barra_estado = px.bar(casos_estado_filtrado.sort_values('Numero_de_Casos', ascending=False), x='Estado', y='Numero_de_Casos', title='Casos por Estado', labels={'Estado': 'Estado', 'Numero_de_Casos': 'Total de Notificações'})
    st.plotly_chart(fig_barra_estado, use_container_width=True)

    # Gráficos Adicionais
    st.header("Análises Adicionais (Seleção Atual)")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribuição por Sexo")
        casos_sexo = df_filtrado['SEXO'].value_counts()
        st.bar_chart(casos_sexo)
    with col2:
        st.subheader("Critério de Confirmação")
        casos_criterio = df_filtrado['CRITERIO_DESC'].value_counts()
        st.bar_chart(casos_criterio)

    if st.checkbox("Mostrar tabela de dados filtrados"):
        st.dataframe(df_filtrado[['NU_ANO', 'ESTADO', 'SEXO', 'IDADE', 'CRITERIO_DESC']]) # Mostra colunas mais legíveis

else:
     if df_analise is not None:
       st.warning("Nenhum dado encontrado para os filtros selecionados.")
