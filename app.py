import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# Configuração da página
st.set_page_config(page_title="Análise de Variação Patrimonial", layout="wide")

st.title("📊 Calculadora de Variação Patrimonial - IRPF")

# --- ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Entradas do Exercício")
    bens_inicial = st.number_input("Bens e Direitos (01/01)", value=0.0)
    bens_final = st.number_input("Bens e Direitos (31/12)", value=0.0)
    dividas_inicial = st.number_input("Dívidas e Ônus (01/01)", value=0.0)
    dividas_final = st.number_input("Dívidas e Ônus (31/12)", value=0.0)
    
    st.divider()
    receitas = st.number_input("Rendimentos Totais (Tributáveis + Isentos)", value=0.0)
    deducoes = st.number_input("Pagamentos e Despesas Consumitivas", value=0.0)

# --- CÁLCULOS ---
patrimonio_liquido_inicial = bens_inicial - dividas_inicial
patrimonio_liquido_final = bens_final - dividas_final
variacao_patrimonial = patrimonio_liquido_final - patrimonio_liquido_inicial

# Lógica: O que você ganhou (receita) menos o que gastou (deduções) deve cobrir o aumento do patrimônio.
disponibilidade_financeira = receitas - deducoes
diferenca_caixa = disponibilidade_financeira - variacao_patrimonial

# Sugestão de Saldo de Caixa para o exercício seguinte
sugestao_caixa_seguinte = max(0.0, diferenca_caixa)

# --- DATA FRAME PARA EXIBIÇÃO ---
dados = [
    {"Descrição": "Patrimônio Líquido Inicial", "Valor": patrimonio_liquido_inicial, "Tipo": "Neutro"},
    {"Descrição": "Patrimônio Líquido Final", "Valor": patrimonio_liquido_final, "Tipo": "Neutro"},
    {"Descrição": "Variação Patrimonial (Aumento/Redução)", "Valor": variacao_patrimonial, "Tipo": "Neutro"},
    {"Descrição": "Receitas e Rendimentos", "Valor": receitas, "Tipo": "Receita"},
    {"Descrição": "Deduções e Despesas", "Valor": deducoes, "Tipo": "Dedução"},
    {"Descrição": "Saldo de Caixa Final (Diferença)", "Valor": diferenca_caixa, "Tipo": "Resultado"},
    {"Descrição": "SUGESTÃO DE SALDO DE CAIXA PARA EXERCÍCIO SEGUINTE", "Valor": sugestao_caixa_seguinte, "Tipo": "Sugestão"}
]

df = pd.DataFrame(dados)

# --- ESTILIZAÇÃO NO STREAMLIT ---
def colorir_linhas(row):
    if row['Tipo'] == 'Receita':
        return ['color: blue'] * len(row)
    elif row['Tipo'] == 'Dedução':
        return ['color: red'] * len(row)
    return [''] * len(row)

st.subheader("Resumo da Variação")
st.table(df.style.apply(colorir_linhas, axis=1))

# --- EXPORTAÇÃO EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Variacao')
    return output.getvalue()

# --- EXPORTAÇÃO PDF (LAUDO) ---
def to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Laudo de Variação Patrimonial", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    
    for _, row in df.iterrows():
        if row['Tipo'] == 'Receita':
            pdf.set_text_color(0, 0, 255) # Azul
        elif row['Tipo'] == 'Dedução':
            pdf.set_text_color(255, 0, 0) # Vermelho
        else:
            pdf.set_text_color(0, 0, 0)   # Preto
            
        texto = f"{row['Descrição']}: R$ {row['Valor']:,.2f}"
        pdf.cell(200, 10, txt=texto, ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# --- BOTÕES DE DOWNLOAD ---
col1, col2 = st.columns(2)

with col1:
    excel_data = to_excel(df)
    st.download_button(label="📥 Baixar Excel", data=excel_data, file_name="variacao_patrimonial.xlsx")

with col2:
    pdf_data = to_pdf(df)
    st.download_button(label="📄 Baixar Laudo PDF", data=pdf_data, file_name="laudo_patrimonial.pdf")

if diferenca_caixa < 0:
    st.error(f"Atenção: Existe uma variação patrimonial a descoberto de R$ {abs(diferenca_caixa):,.2f}. Seus rendimentos não são suficientes para explicar o aumento de patrimônio.")
else:
    st.success("Variação patrimonial compatível com os rendimentos declarados.")
