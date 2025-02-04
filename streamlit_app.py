import streamlit as st
import pandas as pd
import openpyxl

# Função para selecionar a melhor rota com base nos critérios do usuário
def selecionar_rota(df, share, drop_dict, dlr_dict):
    df['Custo_Ajustado'] = df.apply(lambda row: row['Preço'] / ((1 - drop_dict[row['Operadora']]) * dlr_dict[row['Operadora']]), axis=1)
    melhor_linha = df.loc[df['Custo_Ajustado'].idxmin()]
    return melhor_linha['Operadora'], melhor_linha['Preço']

st.title("Precificador de SMS Interativo")

uploaded_file = st.file_uploader("Carregar arquivo de dados (Excel ou CSV)", type=["xlsx", "csv"])
if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    st.success("Arquivo carregado com sucesso!")
    
    st.subheader("Definição de Parâmetros")

    tipo_trafego = st.selectbox("Tipo de Tráfego", ["Marketing", "BET", "Transacional", "OTP"])

    st.subheader("Definir Share por Operadora (%)")
    share = {}
    for operadora in df['Operadora'].unique():
        share[operadora] = st.slider(f"Share para {operadora}:", min_value=0, max_value=100, value=25)
    
    considerar_drop = st.checkbox("Considerar taxa de Drop?")
    drop_dict = {}
    if considerar_drop:
        st.subheader("Definir Drop (%) por Operadora")
        for operadora in df['Operadora'].unique():
            drop_dict[operadora] = st.slider(f"Drop para {operadora}:", min_value=0.0, max_value=1.0, step=0.01, value=0.05)
    else:
        drop_dict = {op: 0 for op in df['Operadora'].unique()}

    st.subheader("Definir DLR (%) por Operadora")
    dlr_dict = {}
    for operadora in df['Operadora'].unique():
        dlr_dict[operadora] = st.slider(f"DLR para {operadora}:", min_value=0.0, max_value=1.0, step=0.01, value=0.95)

    margem_venda = st.number_input("Margem de Venda (%)", min_value=0.0, step=0.1, value=20.0)

    if st.button("Calcular Preço"):
        operadora, custo_base = selecionar_rota(df, share, drop_dict, dlr_dict)
        preco_final = custo_base * (1 + margem_venda / 100)
        st.success(f"Preço unitário do SMS: R$ {preco_final:.4f}\nOperadora selecionada: {operadora}")
else:
    st.warning("Aguardando carregamento dos dados...")
