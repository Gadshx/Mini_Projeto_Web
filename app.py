%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Análise de Dengue no Brasil (2023)", page_icon="🦟", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO (MODIFICADA) ---
# Agora lê o arquivo CSV local que salvamos na célula anterior
@st.cache_data
def carregar_dados_locais():
    try:
        caminho_local_csv = '/content/dados_limpos_para_app.csv' # <-- LÊ O ARQUIVO LOCAL
        df = pd.read_csv(caminho_local_csv, sep=',', encoding='latin-1')
        return df
    except FileNotFoundError:
        st.error("ERRO: O arquivo 'dados_limpos_para_app.csv' não foi encontrado. Execute a célula anterior para criá-lo.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar os dados locais: {e}")
        return None

# --- INTERFACE PRINCIPAL DA APLICAÇÃO ---
st.title("🦟 Dashboard de Análise de Dengue no Brasil - 2023")
st.markdown("Análise interativa dos dados de notificação de Dengue do SINAN.")

# Carrega os dados usando a nova função
df_analise = carregar_dados_locais()

# O resto do código do dashboard permanece igual...
if df_analise is not None:
    st.header("Distribuição de Casos Notificados por Estado")
    casos_por_estado = df_analise.rename(columns={'SG_UF_NOT': 'Estado_Codigo'}) # Renomeia aqui se necessário
    casos_por_estado = casos_por_estado['Estado_Codigo'].value_counts().reset_index()
    casos_por_estado.columns = ['Estado_Codigo', 'Numero_de_Casos']
    mapa_uf = {
        11:'RO', 12:'AC', 13:'AM', 14:'RR', 15:'PA', 16:'AP', 17:'TO', 21:'MA', 22:'PI',
        23:'CE', 24:'RN', 25:'PB', 26:'PE', 27:'AL', 28:'SE', 29:'BA', 31:'MG', 32:'ES',
        33:'RJ', 35:'SP', 41:'PR', 42:'SC', 43:'RS', 50:'MS', 51:'MT', 52:'GO', 53:'DF'
    }
    casos_por_estado['Estado'] = casos_por_estado['Estado_Codigo'].map(mapa_uf)
    fig = px.bar(
        casos_por_estado.sort_values('Numero_de_Casos', ascending=False),
        x='Estado', y='Numero_de_Casos', title='Casos de Dengue por Estado',
        labels={'Estado': 'Estado', 'Numero_de_Casos': 'Total de Notificações'}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.header("Análises Adicionais")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribuição por Sexo")
        casos_sexo = df_analise['CS_SEXO'].value_counts()
        st.bar_chart(casos_sexo)
    with col2:
        st.subheader("Critério de Confirmação")
        # Renomeia coluna criterio se necessário
        casos_criterio = df_analise.rename(columns={'CRITERIO': 'Criterio'})
        casos_criterio = casos_criterio['Criterio'].value_counts()
        st.bar_chart(casos_criterio)
    if st.checkbox("Mostrar tabela de dados limpos"):
        st.dataframe(df_analise)
else:
    st.warning("A aplicação não pode iniciar pois os dados não foram carregados.")
