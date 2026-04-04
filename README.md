# 📊 Laudo de Variação Patrimonial Inteligente (IRPF)

Aplicativo web desenvolvido em Python com a biblioteca Streamlit para automatizar e analisar a Evolução Patrimonial de contribuintes do Imposto de Renda Pessoa Física (IRPF). A ferramenta cruza os dados de bens, dívidas e rendimentos para identificar possíveis riscos de "malha fina" devido a variações a descoberto.

O grande diferencial deste projeto é a integração com a Inteligência Artificial do Google (**Gemini API**), que atua como um Auditor Tributário Preventivo, gerando um parecer automatizado, humanizado e de fácil compreensão para o cliente final.

## 🚀 Principais Funcionalidades

* **Cálculo Automatizado:** Determina instantaneamente a disponibilidade financeira cruzando receitas e deduções com a evolução de bens e direitos.
* **Inteligência Artificial Integrada:** Geração de um parecer técnico simplificado usando o modelo `gemini-2.5-flash`, sugerindo soluções de planejamento tributário dentro do exercício.
* **Exportação Profissional (PDF):** Geração de um laudo formatado em PDF contendo os dados do cliente, tabelas coloridas, gráfico visual e o parecer da IA.
* **Exportação de Dados (Excel):** Download da memória de cálculo em formato `.xlsx` para conferência contábil.
* **Interface Amigável e Adaptada:** Campos de entrada de dados otimizados para aceitar a formatação de moeda brasileira (ex: 1.500,00).
* **Dashboard Visual:** Exibição de métricas instantâneas e gráfico de barras horizontais para fácil interpretação da capacidade de cobertura patrimonial.

## 🛠️ Tecnologias Utilizadas

* **Python:** Linguagem base.
* **Streamlit:** Criação da interface web interativa.
* **Pandas & OpenPyXL:** Manipulação de dados e exportação para planilhas.
* **Matplotlib:** Geração do gráfico comparativo.
* **FPDF:** Construção estruturada do laudo em formato PDF.
* **Google Generative AI:** Conexão com os modelos do Gemini para o parecer inteligente.

## ⚙️ Como executar o projeto localmente

1. Clone este repositório para a sua máquina:
   
bash

`git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)`


2. Instale as dependências necessárias:
   
bash

`pip install -r requirements.txt'`

3. Configure a sua chave da API do Google Gemini:

* Crie uma pasta chamada .streamlit na raiz do projeto.

* Dentro dela, crie um arquivo chamado secrets.toml.

* Insira a sua chave no seguinte formato:

Ini, TOML

`GEMINI_API_KEY = "SUA_CHAVE_AQUI"`

**Atenção:** Certifique-se de que a pasta .streamlit/ esteja incluída no seu arquivo .gitignore para não expor sua chave de API publicamente no GitHub!

4. Execute o aplicativo:

Bash
`streamlit run app.py`


## ☁️ Deploy no Streamlit Cloud


1. Para hospedar o projeto gratuitamente no Streamlit Cloud:

2. Conecte sua conta do GitHub ao Streamlit Community Cloud.

3. Selecione o repositório e o arquivo principal (app.py).

Antes de fazer o deploy, vá em Advanced Settings > Secrets e cole a sua chave da API no mesmo formato utilizado localmente.

Projeto desenvolvido para otimizar o planejamento tributário preventivo e agregar valor à consultoria fiscal.
