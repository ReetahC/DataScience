# 📊 Análise SAF-T - Projeto Completo

Análise abrangente de dados SAF-T (Sistema de Arquivo de Faturas) com pipeline ETL automatizado, testes de qualidade de dados e dashboard interativo com drilldown.

> **🌐 Dashboard Online:** [Ver em Streamlit Cloud](https://share.streamlit.io/ReetahC/DataScience/main/dashboard_drilldown.py)  
> **📦 Repositório:** [github.com/ReetahC/DataScience](https://github.com/ReetahC/DataScience)  
> **👤 Autor:** Rita Costa | **📧 Email:** ritachavescosta@gmail.com

## 📋 Conteúdo do Projeto

### 1️⃣ **Pipeline ETL Reutilizável**
- `etl_pipeline.py` - Classe `PipelineETL` com métodos fluentes
  - Extração de dados Excel
  - Limpeza (prefixos XML, filtros de vendas válidas)
  - Conversão de tipos de dados
  - Remoção de duplicados e nulos
  - Exportação em Excel/CSV

### 2️⃣ **Testes de Qualidade de Dados**
- `data_quality_tests.py` - Suite completaexa com 23 testes automáticos
  - Testes de completude (valores nulos)
  - Consistência (tipos de dados, intervalos)
  - Integridade (duplicados, chaves primárias)
  - Conformidade (valores positivos, datas válidas)
  - Análise de negócio (faturação consistente)
  - Geração de relatórios JSON

### 3️⃣ **Pipeline Completo**
- `pipeline_com_qualidade.py` - Integração ETL + Testes
  - Execução automática do pipeline
  - Testes padrão para SAF-T
  - Exportação de relatórios
  - Função de conveniência `processar_saft()`

### 4️⃣ **Dashboards Interativos**
- `dashboard_streamlit.py` - Dashboard básico
  - KPIs principais
  - Análise de produtos
  - Filtros interativos
  - Exploração de dados

- `dashboard_drilldown.py` - Dashboard avançado com drilldown
  - 📊 Visão Ampla (resumo por categoria)
  - 🔍 Drilldown detalhado (categoria → produtos → temporal)
  - ⚖️ Comparação entre categorias
  - Filtros por data, faturação, produtos
  - Classificação automática em categorias (Pão, Pastelaria, Bebidas, Outros)

### 5️⃣ **Notebook Jupyter**
- `analise_saft_rita_costa.ipynb` - 50 células com:
  - Partes 0-4: Análise conforme especificação
  - Parte 5: Desafios avançados (Análise ABC, Dashboard, Anomalias)
  - Exercício 4.5: Gráfico profissional com trend line
  - Parte 7: Relatório completo
  - Validação automática de completude (23 pontos)

### 6️⃣ **Utilidades**
- `exportar_para_dashboard.py` - Extrai dados do notebook para Excel
- `.gitignore` - Configuração para git

## 🔧 Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Setup Rápido
```bash
# Clonar repositório
git clone https://github.com/ReetahC/DataScience.git
cd DataScience/Analise_SAFT

# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Instalar dependências
pip install pandas numpy matplotlib openpyxl streamlit
```

## 🌐 Deploy

### Streamlit Community Cloud (Recomendado)
1. Vai a [share.streamlit.io](https://share.streamlit.io)
2. Faz login com GitHub
3. Clica em "New app"
4. Seleciona:
   - **Repository:** `ReetahC/DataScience`
   - **Branch:** `main`
   - **Main file path:** `dashboard_drilldown.py`
5. Clica "Deploy!"

**URL da App Online:**  
🔗 https://share.streamlit.io/ReetahC/DataScience/main/dashboard_drilldown.py

## 🚀 Como Usar

### 1. Pipeline ETL
```bash
python pipeline_com_qualidade.py
```
Processa `dados.xlsx` → cria `dados_limpos.xlsx` + relatórios

### 2. Dashboard Drilldown
```bash
streamlit run dashboard_drilldown.py
```
Abre em `http://localhost:8504`

### 3. Dashboard Simples
```bash
streamlit run dashboard_streamlit.py
```
Abre em `http://localhost:8501`

### 4. Notebook Jupyter
```bash
jupyter notebook analise_saft_rita_costa.ipynb
```

## 📊 Dados

Ficheiro: `SAF-T-LIMPO.xlsx` (85.535 registos)

**Colunas:**
- `InvoiceDate` - Data da fatura
- `ProductCode` - Código do produto
- `ProductDescription` - Descrição
- `Quantity` - Quantidade
- `UnitPrice` - Preço unitário
- `CreditAmount` - Valor total
- `LineNumber` - Número da linha
- `TaxPercentage` - Taxa de imposto

**Folhas:**
- Vendas (85.535 linhas)
- Produtos (422 produtos)
- Resumo (análises)

## 📈 Funcionalidades do Dashboard

### Visão Ampla
- 4 KPIs principais
- Cards por categoria com métricas
- Gráficos de distribuição (barras + pizza)

### Drilldown
- 5 abas (uma por categoria)
- Top 10 produtos
- Análise temporal (vendas diárias)
- Tabela completa expansível

### Comparação
- Seleção de categorias
- Gráficos lado-a-lado
- Tabela comparativa

## 🧪 Testes de Qualidade

23 testes automáticos:
- 7 testes de limpeza de dados
- 5 testes de reestruturação
- 6 testes de análise
- 5 testes de relatório

Gera relatório com:
- ✅/❌ status de cada teste
- Percentagens por seção
- Status badge (🏆 Excelente, ✅ Completo, ⚠️ Parcial, ❌ Incompleto)
- Métricas do dataset

## 📂 Estrutura

```
analise_saft/
├── etl_pipeline.py                  # Pipeline ETL
├── data_quality_tests.py            # Testes automáticos
├── pipeline_com_qualidade.py        # Pipeline + Testes
├── dashboard_streamlit.py           # Dashboard básico
├── dashboard_drilldown.py           # Dashboard avançado
├── analise_saft_rita_costa.ipynb    # Notebook (50 células)
├── exportar_para_dashboard.py       # Utilidade
├── SAF-T-LIMPO.xlsx                 # Dados (multi-sheet)
├── .gitignore                       # Git ignore
└── README.md                        # Este ficheiro
```

## 🎯 Características

✅ **Modular** - Componentes independentes reutilizáveis
✅ **Automatizado** - Pipelines com método fluente
✅ **Validado** - 23 testes de qualidade integrados
✅ **Interativo** - Dashboards com filtros dinâmicos
✅ **Profissional** - Gráficos formatados, relatórios JSON
✅ **Documentado** - Docstrings completas, exemplos de uso
✅ **Extensível** - Fácil adicionar novas análises

## 📊 Exemplos de Uso

### Processar ficheiro completo
```python
from pipeline_com_qualidade import processar_saft

processar_saft(
    ficheiro_entrada='SAF-T-LIMPO.xlsx',
    ficheiro_saida='resultado.xlsx',
    pasta_relatorios='relatorios'
)
```

### Usar pipeline ETL
```python
from etl_pipeline import PipelineETL

pipeline = PipelineETL('dados.xlsx')
df_limpo = (pipeline
    .extract()
    .remover_prefixos_xml()
    .filtrar_vendas_validas()
    .converter_tipos()
    .remover_duplicados()
    .obter_dataframe()
)

pipeline.exportar_excel('dados_limpos.xlsx')
pipeline.relatorio()
```

### Executar testes
```python
from data_quality_tests import TestesQualidadeDados
import pandas as pd

df = pd.read_excel('dados.xlsx')
tester = TestesQualidadeDados(df, "Meus Dados")

tester.testar_completude('InvoiceDate', max_nulos_pct=1.0)
tester.testar_valores_positivos('CreditAmount')
tester.testar_datas_validas('InvoiceDate')

relatorio = tester.gerar_relatorio(verbose=True)
```

## 📚 Documentação

Cada módulo possui:
- Docstrings detalhadas
- Exemplos no `if __name__ == "__main__"`
- Comentários inline em seções complexas

## 🤝 Contribuições

Melhorias sugeridas:
- Adicionar gráficos 3D com Plotly
- Integrar com banco de dados
- API FastAPI para o dashboard
- Alertas automáticos de anomalias

## 📝 Licença

Projeto educativo - Universidade

## 👤 Autor

Rita Costa  
DataScience - UF10810

---

**Última atualização:** Fevereiro 2026
