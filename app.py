import streamlit as st
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import os
import tempfile

# Configuração da página
st.set_page_config(page_title="Variação Patrimonial", layout="wide")

# Estilo CSS para melhorar a aparência
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Laudo de Variação Patrimonial")
st.subheader("Análise de Conformidade IRPF")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👤 Dados do Cliente")
    nome_cliente = st.text_input("Nome do Cliente", placeholder="Ex: João Silva")
    cpf_cliente = st.text_input("CPF", placeholder="000.000.000-00")
    
    st.divider()
    st.header("📅 Evolução Patrimonial")
    bens_inicial = st.number_input("Bens e Direitos (Jan/01)", value=0.0, step=1000.0)
    bens_final = st.number_input("Bens e Direitos (Dez/31)", value=0.0, step=1000.0)
    dividas_inicial = st.number_input("Dívidas e Ônus (Jan/01)", value=0.0, step=1000.0)
    dividas_final = st.number_input("Dívidas e Ônus (Dez/31)", value=0.0, step=1000.0)
    
    st.divider()
    st.header("💸 Fluxo de Caixa")
    receitas_trib = st.number_input("Rendimentos Tributáveis", value=0.0, step=500.0)
    receitas_isent = st.number_input("Rendimentos Isentos", value=0.0, step=500.0)
    deducoes = st.number_input("Deduções/Despesas Pagas", value=0.0, step=500.0)

# --- CÁLCULOS MATEMÁTICOS ---
# Variação Patrimonial: $$ \Delta P = (Bens_{final} - Dividas_{final}) - (Bens_{inicial} - Dividas_{inicial}) $$
pl_inicial = bens_inicial - dividas_inicial
pl_final = bens_final - dividas_final
variacao_patrimonial = pl_final - pl_inicial

total_receitas = receitas_trib + receitas_isent
disponibilidade = total_receitas - deducoes
saldo_final = disponibilidade - variacao_patrimonial
sugestao_proximo_ano = max(0.0, saldo_final)

# --- DASHBOARD DE RESUMO ---
col1, col2, col3 = st.columns(3)
col1.metric("Variação Patrimonial", f"R$ {variacao_patrimonial:,.2f}")
col2.metric("Disponibilidade Financeira", f"R$ {disponibilidade:,.2f}")
if saldo_final >= 0:
    col3.metric("Saldo de Caixa", f"R$ {saldo_final:,.2f}", delta="Compatível")
else:
    col3.metric("Saldo de Caixa", f"R$ {saldo_final:,.2f}", delta=f"R$ {abs(saldo_final):,.2f}", delta_color="inverse")

# --- TABELA FORMATADA ---
def formatar_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

dados = [
    {"Descrição": "1. Patrimônio Líquido Inicial", "Valor": pl_inicial, "Cor": "Preto"},
    {"Descrição": "2. Patrimônio Líquido Final", "Valor": pl_final, "Cor": "Preto"},
    {"Descrição": "3. Variação Patrimonial (2 - 1)", "Valor": variacao_patrimonial, "Cor": "Preto"},
    {"Descrição": "4. Rendimentos Tributáveis (+)", "Valor": receitas_trib, "Cor": "Azul"},
    {"Descrição": "5. Rendimentos Isentos (+)", "Valor": receitas_isent, "Cor": "Azul"},
    {"Descrição": "6. Deduções e Despesas (-)", "Valor": deducoes, "Cor": "Vermelho"},
    {"Descrição": "7. Saldo Final de Caixa (4+5-6-3)", "Valor": saldo_final, "Cor": "Preto"},
    {"Descrição": "8. SUGESTÃO DE SALDO PARA EXERCÍCIO SEGUINTE", "Valor": sugestao_proximo_ano, "Cor": "Verde"}
]

df = pd.DataFrame(dados)

def style_df(row):
    if row['Cor'] == 'Azul': return ['color: blue'] * len(row)
    if row['Cor'] == 'Vermelho': return ['color: red'] * len(row)
    if row['Cor'] == 'Verde': return ['font-weight: bold; background-color: #e8f5e9'] * len(row)
    return [''] * len(row)

st.subheader("Memória de Cálculo")
df_view = df.copy()

# 1. Aplicamos a formatação de moeda
df_view['Valor'] = df_view['Valor'].apply(formatar_br)

# 2. O SEGREDO: Aplicamos o estilo no dataframe completo (com a coluna 'Cor')
# e só depois usamos o '.hide' para não mostrar a coluna 'Cor' na tela.
st.table(
    df_view.style.apply(style_df, axis=1)
    .hide(axis='columns', subset=['Cor'])
)

# --- GRÁFICO ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.barh(['Disponibilidade', 'Variação Patrimonial'], [disponibilidade, variacao_patrimonial], color=['#1e88e5', '#e53935'])
ax.set_title("Capacidade de Cobertura Patrimonial")
plt.tight_layout()
st.pyplot(fig)

# --- EXPORTAÇÃO ---

def gerar_pdf(nome, cpf, df_data, figura):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="LAUDO DE VARIAÇÃO PATRIMONIAL", ln=True, align='C')
    pdf.ln(5)
    
    # Identificação
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, f"CLIENTE: {nome.upper() if nome else 'NÃO INFORMADO'}")
    pdf.cell(100, 8, f"CPF: {cpf if cpf else 'NÃO INFORMADO'}", ln=True)
    pdf.line(10, 32, 200, 32)
    pdf.ln(10)
    
    # Tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(130, 10, "DESCRIÇÃO", border=1, fill=True)
    pdf.cell(60, 10, "VALOR", border=1, fill=True, ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    for _, row in df_data.iterrows():
        # Cores no PDF
        if row['Cor'] == 'Azul': pdf.set_text_color(0, 0, 255)
        elif row['Cor'] == 'Vermelho': pdf.set_text_color(255, 0, 0)
        else: pdf.set_text_color(0, 0, 0)
        
        pdf.cell(130, 8, row['Descrição'], border=1)
        pdf.cell(60, 8, formatar_br(row['Valor']), border=1, ln=True, align='R')
    
    # Gráfico (Resolvendo o erro do AttributeError)
    pdf.ln(10)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        figura.savefig(tmpfile.name, format='png', dpi=300)
        pdf.image(tmpfile.name, x=40, w=130)
    os.unlink(tmpfile.name) # Limpa o arquivo temporário
    
    return pdf.output(dest='S').encode('latin-1')

def gerar_excel(df_data, nome, cpf):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_meta = pd.DataFrame([{"Nome": nome, "CPF": cpf}])
        df_meta.to_excel(writer, index=False, sheet_name='Cliente')
        df_data[['Descrição', 'Valor']].to_excel(writer, index=False, sheet_name='Calculo')
    return output.getvalue()

st.divider()
btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    st.download_button("📘 Baixar Laudo em PDF", gerar_pdf(nome_cliente, cpf_cliente, df, fig), "laudo_patrimonial.pdf", "application/pdf")
with btn_col2:
    st.download_button("Excel Planilha de Dados", gerar_excel(df, nome_cliente, cpf_cliente), "dados_patrimoniais.xlsx")
