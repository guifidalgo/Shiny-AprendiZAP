# Projeto Shiny AprendiZAP

Este projeto consiste em um aplicativo de visualização de dados utilizando [Shiny para Python](https://shiny.posit.co/py/), com
foco em análise de interações e cadastros de professores do AprendiZAP.

## Estrutura do Projeto

```
├── app.py                  # Aplicativo Shiny principal
├── data_transformation.py  # Script de transformação dos dados
├── pyproject.toml          # Configuração de dependências (recomendado usar)
├── requirements.txt        # Dependências detalhadas (gerado automaticamente)
├── data/                   # Dados processados (saída)
├── data-raw/               # Dados brutos (entrada)
├── notebooks/              # Notebooks de apoio e exploração
├── assets/                 # Recursos visuais
└── .venv/                  # Ambiente virtual Python (recomendado)
```

## Pré-requisitos

- Python 3.11
- [Shiny para Python](https://shiny.posit.co/py/)
- Recomenda-se o uso de ambiente virtual (`.venv`)

## Instalação do Ambiente

1. **Crie e ative um ambiente virtual:**

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instale as dependências:**
   - Usando o `pyproject.toml` (recomendado):
     ```bash
     pip install -U pip
     pip install uv
     uv pip install -r requirements.txt
     ```
   - Ou diretamente pelo pip:
     ```bash
     pip install -r requirements.txt
     ```

## Execução do Projeto

1. **Disponibilize as bases cruas**

   - Coloque os arquivos de dados brutos no formato `.parquet` na pasta `data-raw/`.
   - Exemplo de arquivos esperados:
     - `data-raw/dim_teachers.parquet`
     - `data-raw/fct_teachers_contents_interactions.parquet`
     - `data-raw/fct_teachers_entries.parquet`

2. **Transforme os dados**

   - Execute o script de transformação:
     ```bash
     python data_transformation.py
     ```
   - Serão gerados os arquivos processados na pasta `data/` necessários para o dashboard.

3. **Execute o aplicativo Shiny**
   - Inicie o app com:
     ```bash
     shiny run
     ```
   - Ou, se preferir, rode diretamente:
     ```bash
     python app.py
     ```

## Notebooks

O diretório `notebooks/` contém notebooks de apoio para exploração e validação dos dados.

## Funcionalidades do Dashboard

O dashboard oferece visualizações interativas dos dados educacionais, incluindo:

- Análises de frequência e engajamento
- Métricas de recência, frequência e duração (RFM)
- Visualizações temporais e comparativas

## Observações

- Os diretórios `data-raw/` e dados processados estão no `.gitignore` e não são versionados.
- Certifique-se de que os arquivos `.parquet` estejam corretamente nomeados e no local correto.
- O projeto utiliza as bibliotecas `pandas`, `pyarrow`, `plotnine` e `shiny`.

---

Em caso de dúvidas, entre em contato.
