import streamlit as st
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import io

# Configuração da página
st.set_page_config(page_title="Laudo de Variação Patrimonial", layout="wide")

st.title("📊 Análise de Variação Patrimonial Profissional")

# --- BARRA LATERAL: IDENTIFICAÇÃO E ENTRADAS ---
with st.sidebar:
    st.header("👤 Identificação do Cliente")
    nome_cliente = st.text_input("Nome Completo")
    cpf_cliente = st.text_input("CPF")
    
    st.divider()
    st.header("💰 Evolução Patrimonial")
    bens_inicial = st.number_input("Bens e Direitos (Início)", value=0.0)
    bens_final = st.number_input("Bens e Direitos (Fim)", value=0.0)
    dividas_inicial = st.number_input("Dívidas e Ônus (Início)", value=0.0)
    dividas_final = st.number_input("Dívidas e Ônus (Fim)", value=0.0)
    
    st.divider()
    st.header("📈 Rendimentos e Gastos")
    receitas_tributaveis = st.number_input("Rendimentos Tributáveis", value=0.0)
    receitas_isentas = st.number_input("Rendimentos Isentos/Exclusivos", value=0.0)
    deducoes = st.number_input("Deduções e Despesas Consumitivas", value=0.0)

# --- CÁLCULOS ---
total_receitas = receitas_tributaveis + receitas_isentas
pl_inicial = bens_inicial - dividas_inicial
pl_final = bens_final - dividas_final
variacao_patrimonial = pl_final - pl_inicial
disponibilidade = total_receitas - deducoes
diferenca_caixa = disponibilidade - variacao_patrimonial
sugestao_caixa = max(0.0, diferenca_caixa)

# --- INTERFACE PRINCIPAL ---
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.info(f"**Cliente:** {nome_cliente if nome_cliente else 'Não informado'}")
with col_info2:
    st.info(f"**CPF:** {cpf_cliente if cpf_cliente else 'Não informado'}")

# Preparação dos dados para a tabela
dados = [
    {"Descrição": "Patrimônio Líquido Inicial", "Valor": pl_inicial, "Tipo": "Neutro"},
    {"Descrição": "Patrimônio Líquido Final", "Valor": pl_final, "Tipo": "Neutro"},
    {"Descrição": "Variação Patrimonial do Período", "Valor": variacao_patrimonial, "Tipo": "Neutro"},
    {"Descrição": "Rendimentos Tributáveis (+)", "Valor": receitas_tributaveis, "Tipo": "Receita"},
    {"Descrição": "Rendimentos Isentos (+)", "Valor": receitas_isentas, "Tipo": "Receita"},
    {"Descrição": "Deduções e Despesas (-)", "Valor": deducoes, "Tipo": "Dedução"},
    {"Descrição": "Saldo de Caixa Final", "Valor": diferenca_caixa, "Tipo": "Resultado"},
    {"Descrição": "SUGESTÃO DE SALDO DE CAIXA (PRÓX. EXERCÍCIO)", "Valor": sugestao_caixa, "Tipo": "Sugestão"}
]

df = pd.DataFrame(dados)

# Formatação de Moeda para exibição
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

df_display = df.copy()
df_display['Valor'] = df_display['Valor'].apply(formatar_moeda)

# Estilização da tabela Streamlit
def colorir_linhas(row):
    if row['Tipo'] == 'Receita': return ['color: blue'] * len(row)
    if row['Tipo'] == 'Dedução': return ['color: red'] * len(row)
    return [''] * len(row)

st.subheader("Resumo da Variação")
st.table(df_display.style.apply(colorir_linhas, axis=1))

# --- GRÁFICO SIMPLES ---
st.subheader("Visualização da Capacidade Financeira")
fig, ax = plt.subplots(figsize=(8, 4))
labels = ['Disponibilidade', 'Variação Patrimonial']
valores = [disponibilidade, variacao_patrimonial]
ax.bar(labels, valores, color=['skyblue', 'salmon'])
ax.set_ylabel('Valores em R$')
st.pyplot(fig)

# --- FUNÇÕES DE EXPORTAÇÃO ---

def gerar_excel(df, nome, cpf):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        info_df = pd.DataFrame([{"Cliente": nome, "CPF": cpf}])
        info_df.to_excel(writer, index=False, sheet_name='Identificacao')
        df.to_excel(writer, index=False, sheet_name='Resumo_Calculo')
    return output.getvalue()

def gerar_pdf(df, nome, cpf, fig):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Laudo de Variação Patrimonial", ln=True, align='C')
    
    # Identificação
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    pdf.cell(200, 8, txt=f"Cliente: {nome}", ln=True)
    pdf.cell(200, 8, txt=f"CPF: {cpf}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Tabela no PDF
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(130, 10, "Descrição", border=1)
    pdf.cell(60, 10, "Valor", border=1, ln=True)
    
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        if row['Tipo'] == 'Receita': pdf.set_text_color(0, 0, 255)
        elif row['Tipo'] == 'Dedução': pdf.set_text_color(255, 0, 0)
        else: pdf.set_text_color(0, 0, 0)
        
        pdf.cell(130, 8, row['Descrição'], border=1)
        pdf.cell(60, 8, formatar_moeda(row['Valor']), border=1, ln=True)
    
    # Inserir Gráfico no PDF
    pdf.ln(10)
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    pdf.image(img_buf, x=50, w=110)
    
    return pdf.output(dest='S').encode('latin-1')

# --- BOTÕES DE DOWNLOAD ---
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button("📥 Exportar Excel", gerar_excel(df, nome_cliente, cpf_cliente), "relatorio_patrimonial.xlsx")
with col_dl2:
    st.download_button("📄 Exportar Laudo PDF", gerar_pdf(df, nome_cliente, cpf_cliente, fig), "laudo_patrimonial.pdf")
