import streamlit as st
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import os
import tempfile
import google.generativeai as genai

st.set_page_config(page_title="Variação Patrimonial IA", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Laudo de Variação Patrimonial Inteligente")
st.subheader("Análise de Conformidade IRPF com Inteligência Artificial")

# Configuração Segura da API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    api_configurada = True
except Exception:
    api_configurada = False
    st.warning("⚠️ Chave de API não encontrada nos Secrets. A análise com IA está desativada.")

if 'texto_ia' not in st.session_state:
    st.session_state.texto_ia = ""

# --- FUNÇÃO DE CONVERSÃO DE MOEDA ---
def tratar_moeda(valor_digitado):
    if not valor_digitado:
        return 0.0
    # Remove R$, espaços e o ponto de milhar. Troca a vírgula por ponto para o Python calcular.
    texto_limpo = str(valor_digitado).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(texto_limpo)
    except ValueError:
        return 0.0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👤 Dados do Cliente")
    nome_cliente = st.text_input("Nome do Cliente", placeholder="Ex: João Silva")
    cpf_cliente = st.text_input("CPF", placeholder="000.000.000-00")
    
    st.divider()
    st.header("📅 Evolução Patrimonial")
    st.caption("Pode digitar usando pontos e vírgulas (Ex: 1.500,50)")
    
    bens_inicial_str = st.text_input("Bens e Direitos (Jan/01)", value="0,00")
    bens_final_str = st.text_input("Bens e Direitos (Dez/31)", value="0,00")
    dividas_inicial_str = st.text_input("Dívidas e Ônus (Jan/01)", value="0,00")
    dividas_final_str = st.text_input("Dívidas e Ônus (Dez/31)", value="0,00")
    
    st.divider()
    st.header("💸 Fluxo de Caixa")
    receitas_trib_str = st.text_input("Rendimentos Tributáveis", value="0,00")
    receitas_isent_str = st.text_input("Rendimentos Isentos", value="0,00")
    deducoes_str = st.text_input("Deduções/Despesas Pagas", value="0,00")

# --- CONVERSÃO E CÁLCULOS MATEMÁTICOS ---
bens_inicial = tratar_moeda(bens_inicial_str)
bens_final = tratar_moeda(bens_final_str)
dividas_inicial = tratar_moeda(dividas_inicial_str)
dividas_final = tratar_moeda(dividas_final_str)
receitas_trib = tratar_moeda(receitas_trib_str)
receitas_isent = tratar_moeda(receitas_isent_str)
deducoes = tratar_moeda(deducoes_str)

pl_inicial = bens_inicial - dividas_inicial
pl_final = bens_final - dividas_final
variacao_patrimonial = pl_final - pl_inicial

total_receitas = receitas_trib + receitas_isent
disponibilidade = total_receitas - deducoes
saldo_final = disponibilidade - variacao_patrimonial
sugestao_proximo_ano = max(0.0, saldo_final)

# --- DASHBOARD ---
col1, col2, col3 = st.columns(3)
col1.metric("Variação Patrimonial", f"R$ {variacao_patrimonial:,.2f}")
col2.metric("Disponibilidade Financeira", f"R$ {disponibilidade:,.2f}")
if saldo_final >= 0:
    col3.metric("Saldo de Caixa", f"R$ {saldo_final:,.2f}", delta="Compatível")
else:
    col3.metric("Saldo de Caixa", f"R$ {saldo_final:,.2f}", delta=f"R$ {abs(saldo_final):,.2f}", delta_color="inverse")

# --- TABELA ---
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
df_view['Valor'] = df_view['Valor'].apply(formatar_br)
st.table(df_view.style.apply(style_df, axis=1).hide(axis='columns', subset=['Cor']))

# --- ANÁLISE COM INTELIGÊNCIA ARTIFICIAL ---
st.divider()
st.subheader("🤖 Consultoria IA")

if api_configurada:
    if st.button("Gerar Parecer Inteligente"):
        with st.spinner("Analisando saúde fiscal do cliente..."):
            try:
                # O modelo atualizado e rápido
                modelo = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = f"""
                Aja como um Auditor Tributário Preventivo de alto nível, que joga no time do cliente. 
                Sua missão é ter o rigor de um fiscal da Receita Federal para identificar riscos, mas transmitir a mensagem de forma humanizada, profissional e extremamente simplificada.
                
                Analise os dados financeiros do exercício atual deste cliente:
                - Variação do Patrimônio (Evolução de Bens - Dívidas): R$ {variacao_patrimonial}
                - Disponibilidade Financeira (Receitas - Despesas): R$ {disponibilidade}
                - Diferença final (Risco de variação a descoberto): R$ {saldo_final}
                
                Instruções:
                Escreva 2 parágrafos curtos e diretos ao ponto.
                No primeiro, faça um diagnóstico claro: a evolução patrimonial faz sentido com o dinheiro que entrou? Existe algum risco de malha fina?
                No segundo, sugira uma (1) ação prática e legal que o cliente pode tomar AINDA NESTE ANO para ajustar a declaração ou justificar a diferença.
                Regra de Ouro: Evite jargões contábeis complexos (o famoso "economês"). Traduza o cenário para uma linguagem didática e de fácil compreensão para quem não entende nada de contabilidade.
                """
                
                resposta = modelo.generate_content(prompt)
                st.session_state.texto_ia = resposta.text
            except Exception as e:
                st.error(f"Erro ao gerar análise: {e}")

if st.session_state.texto_ia:
    st.info(st.session_state.texto_ia)
    
# --- GRÁFICO E EXPORTAÇÃO ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.barh(['Disponibilidade', 'Variação Patrimonial'], [disponibilidade, variacao_patrimonial], color=['#1e88e5', '#e53935'])
ax.set_title("Capacidade de Cobertura Patrimonial")
plt.tight_layout()

def gerar_pdf(nome, cpf, df_data, figura, parecer_ia):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="LAUDO DE VARIAÇÃO PATRIMONIAL", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 8, f"CLIENTE: {nome.upper() if nome else 'NÃO INFORMADO'}")
    pdf.cell(100, 8, f"CPF: {cpf if cpf else 'NÃO INFORMADO'}", ln=True)
    pdf.line(10, 32, 200, 32)
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(130, 8, "DESCRIÇÃO", border=1, fill=True)
    pdf.cell(60, 8, "VALOR", border=1, fill=True, ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    for _, row in df_data.iterrows():
        if row['Cor'] == 'Azul': pdf.set_text_color(0, 0, 255)
        elif row['Cor'] == 'Vermelho': pdf.set_text_color(255, 0, 0)
        else: pdf.set_text_color(0, 0, 0)
        pdf.cell(130, 8, row['Descrição'], border=1)
        pdf.cell(60, 8, formatar_br(row['Valor']), border=1, ln=True, align='R')
    
    pdf.ln(5)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        figura.savefig(tmpfile.name, format='png', dpi=300)
        pdf.image(tmpfile.name, x=40, w=130)
    os.unlink(tmpfile.name)
    
    if parecer_ia:
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 8, txt="Parecer Tecnico e Sugestao Profissional:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, txt=parecer_ia.encode('latin-1', 'replace').decode('latin-1'))

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
    st.download_button("📘 Baixar Laudo em PDF", gerar_pdf(nome_cliente, cpf_cliente, df, fig, st.session_state.texto_ia), "laudo_patrimonial.pdf", "application/pdf")
with btn_col2:
    st.download_button("📊 Excel Planilha de Dados", gerar_excel(df, nome_cliente, cpf_cliente), "dados_patrimoniais.xlsx")
