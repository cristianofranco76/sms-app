import streamlit as st
import pandas as pd

def selecionar_rota(df, modo='normal'):
    """
    Seleciona a melhor operadora com base na métrica de custo efetivo.
    O custo efetivo é calculado como: custo / (1 - drop)
    """
    df['Custo_Efetivo'] = df['Preço'] / (1 - df['Drop'])
    melhor_linha = df.loc[df['Custo_Efetivo'].idxmin()]
    return melhor_linha['Operadora'], melhor_linha['Preço']

def calcular_preco(custo_base, margem_venda):
    """
    Calcula o preço final do SMS com base no custo base e na margem de venda.
    """
    preco_final = custo_base * (1 + margem_venda / 100)
    return round(preco_final, 4)

st.title("Precificador de SMS Interativo")

st.markdown("""
Carregue a base de dados contendo as seguintes colunas:
- **Rota**: identificação da rota
- **Operadora**: nome da operadora
- **Preço**: custo por SMS para a operadora
- **Drop**: taxa de drop (ex: 0.1 para 10%)
""")

uploaded_file = st.file_uploader("Carregar arquivo", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('xlsx'):
            df = pd.read_excel(uploaded_file, sheet_name="Tabela_Rotas")
        else:
            df = pd.read_csv(uploaded_file)
        
        df = df.iloc[3:].reset_index(drop=True)
        df.columns = ["Rota", "Tipo", "Operadora", "Share %", "Preço", "Margem", "Drop", "PMU", "Fornecedor"]
        df = df.dropna(subset=["Rota", "Operadora", "Preço", "Drop"])
        
        st.success("Arquivo carregado com sucesso!")
        st.write("Visualização dos dados:", df)
        
        rotas = df['Rota'].unique()
        rota_selecionada = st.selectbox("Selecione a rota desejada:", rotas)
        df_filtrado = df[df['Rota'] == rota_selecionada]
        
        st.subheader("Parâmetros de Entrada")
        tipo_trafego = st.selectbox("Tipo de Tráfego", ["Marketing", "BET", "Transacional", "OTP"])
        margem_venda = st.number_input("Margem de Venda (%)", min_value=0.0, step=0.1, value=20.0)
        
        if st.button("Calcular Preço"):
            operadora, custo_base = selecionar_rota(df_filtrado)
            preco_final = calcular_preco(custo_base, margem_venda)
            st.success(f"Preço unitário do SMS: R$ {preco_final:.4f}\nOperadora selecionada: {operadora}")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Por favor, carregue um arquivo com os dados para continuar.")
