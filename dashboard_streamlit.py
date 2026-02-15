"""
Dashboard Interativo SAF-T em Streamlit
Visualização e análise exploratória dos dados de vendas
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============ CONFIGURAÇÃO STREAMLIT ============
st.set_page_config(
    page_title="Dashboard SAF-T",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos customizados
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 14px;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)


# ============ FUNÇÕES DE CARREGAMENTO ============
@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    """Carrega dados com cache - trata erro de ficheiro bloqueado"""
    try:
        if caminho.endswith('.xlsx'):
            try:
                df = pd.read_excel(caminho)
            except PermissionError:
                # Se ficheiro está bloqueado, tentar com engine openpyxl
                import openpyxl
                df = pd.read_excel(caminho, engine='openpyxl')
        elif caminho.endswith('.csv'):
            df = pd.read_csv(caminho)
        else:
            st.error(f"Formato não suportado: {caminho}")
            return None
        
        # Converter datas
        for col in df.columns:
            if 'date' in col.lower() or 'data' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except PermissionError:
        st.error(f"❌ Ficheiro '{caminho}' está bloqueado (aberto noutro programa)")
        st.info("💡 Solução: Fecha o ficheiro em Excel/LibreOffice e tenta novamente")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None


# ============ MÉTRICAS KPI ============
def exibir_kpis(df: pd.DataFrame) -> None:
    """Exibe KPIs principais"""
    st.subheader("📈 KPIs Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        registos = len(df)
        st.metric("📋 Total de Produtos", f"{registos:,}")
    
    with col2:
        if 'ProductCode' in df.columns:
            unicos = df['ProductCode'].nunique()
            st.metric("📦 Códigos Únicos", f"{unicos:,}")
        else:
            st.metric("📦 Códigos Únicos", "N/A")
    
    with col3:
        if 'ProductDescription' in df.columns:
            descricoes = df['ProductDescription'].nunique()
            st.metric("📝 Descrições Únicas", f"{descricoes:,}")
        else:
            st.metric("📝 Descrições Únicas", "N/A")
    
    with col4:
        memoria = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("💾 Tamanho", f"{memoria:.2f} MB")


# ============ ANÁLISE TEMPORAL ============
def analise_temporal(df: pd.DataFrame) -> None:
    """Análise de vendas ao longo do tempo"""
    st.subheader("📅 Análise Temporal")
    
    if 'InvoiceDate' not in df.columns:
        st.info("ℹ️ Este dataset não contém datas (coluna InvoiceDate)")
        st.write("**Colunas disponíveis:**")
        st.write(", ".join(df.columns))
        return
    
    col1, col2 = st.columns(2)
    
    # Vendas por dia
    with col1:
        vendas_dia = df.groupby(df['InvoiceDate'].dt.date)['CreditAmount'].agg(['sum', 'count', 'mean'])
        vendas_dia.columns = ['Faturação', 'Transações', 'Ticket Médio']
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(vendas_dia.index, vendas_dia['Faturação'], marker='o', linewidth=2, color='#1f77b4')
        ax.fill_between(range(len(vendas_dia)), vendas_dia['Faturação'], alpha=0.3, color='#1f77b4')
        ax.set_title("Faturação Diária", fontsize=14, fontweight='bold')
        ax.set_xlabel("Data")
        ax.set_ylabel("Faturação (€)")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Vendas por mês
    with col2:
        df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
        vendas_mes = df.groupby('YearMonth')['CreditAmount'].agg(['sum', 'count', 'mean'])
        vendas_mes.columns = ['Faturação', 'Transações', 'Ticket Médio']
        
        fig, ax = plt.subplots(figsize=(12, 5))
        vendas_mes['Faturação'].plot(kind='bar', ax=ax, color='#2ca02c', edgecolor='black')
        ax.set_title("Faturação Mensal", fontsize=14, fontweight='bold')
        ax.set_xlabel("Mês")
        ax.set_ylabel("Faturação (€)")
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)


# ============ ANÁLISE POR CATEGORIA ============
def analise_categorias(df: pd.DataFrame) -> None:
    """Análise por categoria de produto"""
    st.subheader("📦 Análise por Categoria")
    
    if 'ProductDescription' not in df.columns or 'CreditAmount' not in df.columns:
        st.warning("Colunas necessárias não encontradas")
        return
    
    col1, col2 = st.columns(2)
    
    # Classificar categorias logicamente
    def classificar_categoria(descricao):
        descricao_lower = str(descricao).lower()
        if any(word in descricao_lower for word in ['pão', 'broa', 'baguete']):
            return 'Pão'
        elif any(word in descricao_lower for word in ['pastel', 'bolo', 'tarte', 'croissant']):
            return 'Pastelaria'
        elif any(word in descricao_lower for word in ['agua', 'café', 'chá', 'suco', 'bebida']):
            return 'Bebidas'
        else:
            return 'Outros'
    
    df['Categoria'] = df['ProductDescription'].apply(classificar_categoria)
    
    # Gráfico de pizza
    with col1:
        vendas_categoria = df.groupby('Categoria')['CreditAmount'].sum()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        cores = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        wedges, texts, autotexts = ax.pie(
            vendas_categoria.values,
            labels=vendas_categoria.index,
            autopct='%1.1f%%',
            colors=cores,
            startangle=90
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax.set_title("Distribuição de Vendas por Categoria", fontsize=14, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Tabela detalhada
    with col2:
        resumo_cat = df.groupby('Categoria')['CreditAmount'].agg(['sum', 'count', 'mean'])
        resumo_cat.columns = ['Faturação (€)', 'Transações', 'Ticket Médio (€)']
        resumo_cat['% do Total'] = (resumo_cat['Faturação (€)'] / resumo_cat['Faturação (€)'].sum() * 100).round(2)
        resumo_cat = resumo_cat.sort_values('Faturação (€)', ascending=False)
        
        st.dataframe(
            resumo_cat.style.format({
                'Faturação (€)': '€{:,.2f}',
                'Ticket Médio (€)': '€{:.2f}',
                '% do Total': '{:.1f}%'
            }),
            use_container_width=True
        )


# ============ TOP PRODUTOS ============
def analise_produtos(df: pd.DataFrame) -> None:
    """Análise dos produtos mais vendidos"""
    st.subheader("🏆 Top Produtos")
    
    if 'ProductDescription' not in df.columns or 'CreditAmount' not in df.columns:
        st.warning("Colunas necessárias não encontradas")
        return
    
    top_n = st.slider("Quantos produtos?", min_value=5, max_value=20, value=10)
    
    col1, col2 = st.columns(2)
    
    # Top por faturação
    with col1:
        top_faturacao = df.groupby('ProductDescription')['CreditAmount'].sum().nlargest(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        top_faturacao.plot(kind='barh', ax=ax, color='#1f77b4', edgecolor='black')
        ax.set_title(f"Top {top_n} Produtos - Faturação", fontsize=14, fontweight='bold')
        ax.set_xlabel("Faturação (€)")
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Top por quantidade
    with col2:
        top_qtd = df.groupby('ProductDescription')['ProductDescription'].count().nlargest(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        top_qtd.plot(kind='barh', ax=ax, color='#2ca02c', edgecolor='black')
        ax.set_title(f"Top {top_n} Produtos - Quantidade", fontsize=14, fontweight='bold')
        ax.set_xlabel("Transações")
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig)


# ============ ANÁLISE ABC ============
def analise_abc(df: pd.DataFrame) -> None:
    """Classificação ABC dos produtos"""
    st.subheader("📊 Análise ABC")
    
    if 'ProductDescription' not in df.columns or 'CreditAmount' not in df.columns:
        st.warning("Colunas necessárias não encontradas")
        return
    
    # Calcular faturação por produto
    faturacao_prod = df.groupby('ProductDescription')['CreditAmount'].sum().sort_values(ascending=False)
    faturacao_total = faturacao_prod.sum()
    
    # Calcular acumulado
    faturacao_acumulada = faturacao_prod.cumsum()
    pct_acumulado = (faturacao_acumulada / faturacao_total * 100)
    
    # Classificar
    def classificar_abc(pct):
        if pct <= 80:
            return 'A'
        elif pct <= 95:
            return 'B'
        else:
            return 'C'
    
    classificacao = pct_acumulado.apply(classificar_abc)
    
    # Criar DataFrame
    abc_df = pd.DataFrame({
        'Produto': faturacao_prod.index,
        'Faturação': faturacao_prod.values,
        'Faturação Acumulada': faturacao_acumulada.values,
        '% Acumulado': pct_acumulado.values,
        'Classe': classificacao.values
    }).reset_index(drop=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de Pareto
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Cores por classe
        cores = ['#ff6b6b' if c == 'A' else '#4ecdc4' if c == 'B' else '#95e1d3' 
                for c in abc_df['Classe']]
        
        ax.bar(range(len(abc_df)), abc_df['Faturação'], color=cores, edgecolor='black', alpha=0.7)
        ax.set_title("Curva de Pareto (Análise ABC)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Produtos (ordenados por faturação)")
        ax.set_ylabel("Faturação (€)")
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adicionar linha de referência para 80%
        ax.axhline(y=faturacao_total * 0.8, color='red', linestyle='--', linewidth=2, label='80% do total')
        ax.legend()
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Resumo das classes
        resumo_abc = abc_df.groupby('Classe').agg({
            'Produto': 'count',
            'Faturação': 'sum'
        })
        resumo_abc.columns = ['Qtd Produtos', 'Faturação (€)']
        
        st.dataframe(
            resumo_abc.style.format({'Faturação (€)': '€{:,.2f}'}),
            use_container_width=True
        )
    
    # Tabela completa
    st.write("#### Detalhes Completos")
    st.dataframe(
        abc_df.style.format({
            'Faturação': '€{:,.2f}',
            'Faturação Acumulada': '€{:,.2f}',
            '% Acumulado': '{:.1f}%'
        }),
        use_container_width=True,
        height=400
    )


# ============ ANÁLISE EXPLORATÓRIA ============
def analise_exploratoria(df: pd.DataFrame) -> None:
    """Análise exploratória dos dados"""
    st.subheader("🔍 Análise Exploratória")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Informações do Dataset**")
        st.write(f"Linhas: {len(df):,}")
        st.write(f"Colunas: {len(df.columns)}")
        st.write(f"Tamanho: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    with col2:
        st.write("**Colunas Disponíveis**")
        for col in df.columns:
            st.write(f"• {col}")
    
    with col3:
        st.write("**Tipo de Dados**")
        for col in df.columns:
            st.write(f"• {col}: {df[col].dtype}")


# ============ ANÁLISE DE PRODUTOS ============
def analise_produtos_simples(df: pd.DataFrame) -> None:
    """Análise dos produtos"""
    st.subheader("📦 Análise de Produtos")
    
    if 'ProductDescription' not in df.columns and 'ProductCode' not in df.columns:
        st.warning("Colunas de produtos não encontradas")
        return
    
    # Escolher qual coluna usar
    se_temos_desc = 'ProductDescription' in df.columns
    se_temos_code = 'ProductCode' in df.columns
    
    if se_temos_desc:
        coluna_analise = 'ProductDescription'
    elif se_temos_code:
        coluna_analise = 'ProductCode'
    else:
        return
    
    # Produtos únicos
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Produtos Únicos**")
        unicos = df[coluna_analise].nunique()
        st.metric("Total", unicos)
        
        # Lista dos produtos
        with st.expander("Ver lista completa"):
            produtos = sorted(df[coluna_analise].unique())
            for prod in produtos:
                st.write(f"• {prod}")
    
    with col2:
        st.write(f"**Frequência de {coluna_analise}**")
        
        frequencia = df[coluna_analise].value_counts().head(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        frequencia.plot(kind='barh', ax=ax, color='#2ca02c', edgecolor='black')
        ax.set_title(f"Top 15 {coluna_analise}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Frequência")
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        st.pyplot(fig)


# ============ FILTROS INTERATIVOS ============
def painel_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Painel de filtros na sidebar"""
    st.sidebar.header("🔧 Filtros")
    
    df_filtrado = df.copy()
    
    # Filtro de produto
    if 'ProductDescription' in df.columns:
        with st.sidebar.expander("📝 Descrição"):
            produtos = sorted(df['ProductDescription'].unique())
            produtos_selecionados = st.multiselect(
                "Selecionar descrições",
                options=produtos,
                default=produtos
            )
            df_filtrado = df_filtrado[df_filtrado['ProductDescription'].isin(produtos_selecionados)]
    
    # Filtro de código de produto
    if 'ProductCode' in df.columns:
        with st.sidebar.expander("📦 Código"):
            codigos = sorted(df['ProductCode'].unique())
            codigos_selecionados = st.multiselect(
                "Selecionar códigos",
                options=codigos,
                default=codigos
            )
            df_filtrado = df_filtrado[df_filtrado['ProductCode'].isin(codigos_selecionados)]
    
    # Mostrar estatísticas dos filtros
    st.sidebar.divider()
    st.sidebar.write("**Dados Após Filtros:**")
    st.sidebar.metric("Registos", f"{len(df_filtrado):,}")
    
    return df_filtrado


# ============ PÁGINA PRINCIPAL ============
def main():
    # Header
    st.title("📊 Dashboard SAF-T")
    st.markdown("Análise interativa de dados de vendas")
    
    # Selector de ficheiro
    with st.sidebar:
        st.header("📁 Dados")
        
        # Procurar ficheiros disponíveis
        ficheiros_disponiveis = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.csv'))
        ficheiros_disponiveis = [f.name for f in ficheiros_disponiveis]
        
        if ficheiros_disponiveis:
            ficheiro_selecionado = st.selectbox(
                "Selecionar ficheiro",
                options=ficheiros_disponiveis,
                index=0 if 'dados_limpos.xlsx' in ficheiros_disponiveis else 0
            )
        else:
            st.error("Nenhum ficheiro Excel ou CSV encontrado na pasta")
            st.stop()
    
    # Carregar dados
    df = carregar_dados(ficheiro_selecionado)
    
    if df is None or len(df) == 0:
        st.error("Não foi possível carregar os dados")
        st.stop()
    
    # Aplicar filtros
    df_filtrado = painel_filtros(df)
    
    if len(df_filtrado) == 0:
        st.warning("Nenhum dado corresponde aos filtros selecionados")
        st.stop()
    
    # Mostrar dashboard
    st.divider()
    
    # Abas simplificadas para dados disponíveis
    tab1, tab2, tab3 = st.tabs([
        "📈 KPIs",
        "📦 Produtos",
        "🔍 Exploração"
    ])
    
    with tab1:
        exibir_kpis(df_filtrado)
    
    with tab2:
        analise_produtos_simples(df_filtrado)
    
    with tab3:
        analise_exploratoria(df_filtrado)
        st.divider()
        analise_temporal(df_filtrado)
    
    # Footer
    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: #888; font-size: 12px;'>
        Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
        Registos: {len(df_filtrado):,} | Ficheiro: {ficheiro_selecionado}
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
