# 📊 Dashboard SAF-T em Streamlit

Dashboard interativo para análise de dados SAF-T com visualizações, filtros e análises automáticas.

## 🚀 Instalação

### 1. Instalar Streamlit
```bash
pip install streamlit
```

### 2. Ou instalar todas as dependências
```bash
pip install streamlit pandas matplotlib numpy openpyxl
```

## 📂 Ficheiros Necessários

O dashboard procura automaticamente por ficheiros Excel ou CSV na mesma pasta:
- `dados_limpos.xlsx` (recomendado)
- `dados.xlsx`
- Ou qualquer outro `.xlsx` ou `.csv`

## ▶️ Executar o Dashboard

### Windows (PowerShell)
```powershell
streamlit run dashboard_streamlit.py
```

### macOS/Linux (Terminal)
```bash
streamlit run dashboard_streamlit.py
```

O dashboard abrirá automaticamente no browser em `http://localhost:8501`

## 📊 Funcionalidades

### 🔍 Filtros Interativos (Sidebar)
- **📅 Período**: Escolher intervalo de datas
- **💰 Faturação**: Filtrar por faixa de valores
- **📦 Produtos**: Selecionar produtos específicos

### 📈 Abas do Dashboard

#### 1. **KPIs**
- Total de registos
- Faturação total
- Ticket médio
- Produtos únicos
- Estatísticas detalhadas

#### 2. **Análise Temporal**
- Faturação diária (gráfico de linha)
- Faturação mensal (gráfico de barras)
- Tendências ao longo do tempo

#### 3. **Categorias**
- Distribuição por categoria (pie chart)
- Faturação por categoria
- Número de transações por categoria
- Ticket médio por categoria

#### 4. **Top Produtos**
- Top N produtos por faturação (customizável)
- Top N produtos por quantidade de vendas
- Slider para escolher quantos produtos mostrar

#### 5. **Análise ABC**
- Curva de Pareto
- Classificação A/B/C dos produtos
- Tabela detalhada com acumulado

## 🎨 Características

✅ **Responsivo** - Adapta-se a diferentes tamanhos de ecrã  
✅ **Interativo** - Filtros em tempo real  
✅ **Rápido** - Cache de dados para melhor performance  
✅ **Completo** - Múltiplas vistas e análises  
✅ **Automático** - Detecta automaticamente as colunas disponíveis  

## 🔧 Customizações

### Mudar o ficheiro padrão
Editar a linha 287:
```python
index=0 if 'dados_limpos.xlsx' in ficheiros_disponiveis else 0
```

### Adicionar mais análises
Criar uma função nova e adicionar uma aba:
```python
def minha_analise(df):
    st.write("Minha análise")

# Na main():
with st.tabs(...):
    with aba_nova:
        minha_analise(df_filtrado)
```

## 💡 Dicas de Uso

1. **Usar dados limpos**: Executar primeiro o pipeline ETL para gerar `dados_limpos.xlsx`
2. **Filtros múltiplos**: Combinar filtros para análises específicas
3. **Exportar**: Clicar no menu "⋯" → "Download as PNG" para guardar gráficos
4. **Mobile**: O dashboard funciona em mobile (sidebar recolhida)

## ⚙️ Requisitos de Dados

O dashboard espera colunas padrão SAF-T:
- `InvoiceDate` - Data da fatura
- `CreditAmount` - Valor faturado
- `ProductCode` - Código do produto
- `ProductDescription` - Descrição do produto
- `Quantity` - Quantidade

(Se não existir, o dashboard adapta-se e mostra apenas o que está disponível)

## 🐛 Resolução de Problemas

### Erro: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### Dashboard não encontra ficheiros
- Verificar se os ficheiros estão na mesma pasta que `dashboard_streamlit.py`
- Usar nomes de ficheiros sem acentos

### Gráficos não aparecem
- Certificar que as colunas esperadas existem no ficheiro
- Verificar se os dados não estão com valores nulos

## 📝 Exemplo de Uso Completo

```bash
# 1. Limpar dados (opcional)
python pipeline_com_qualidade.py

# 2. Abrir dashboard
streamlit run dashboard_streamlit.py
```

## 🌐 Deploy

Para colocar o dashboard online (gratuito):

### Streamlit Cloud
1. Fazer push do código para GitHub
2. Ir a https://streamlit.io/cloud
3. Clicar "Deploy an app"
4. Selecionar o repositório
5. Pronto! 🚀

## 📞 Suporte

Se tiver problemas:
1. Verificar se o ficheiro de dados existe
2. Verificar se as dependências estão instaladas
3. Executar `streamlit run --logger.level=debug dashboard_streamlit.py`
