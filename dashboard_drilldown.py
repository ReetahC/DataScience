"""
Dashboard SAF-T com Drilldown Interativo
Visão ampla → Visão detalhada com filtros por categoria
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============ CONFIGURAÇÃO ============
st.set_page_config(
    page_title="Dashboard SAF-T - Drilldown",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .category-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid;
        margin: 10px 0;
    }
    .card-a { border-color: #ff6b6b; background-color: #ffe0e0; }
    .card-b { border-color: #4ecdc4; background-color: #e0f7f6; }
    .card-c { border-color: #95e1d3; background-color: #e8f9f6; }
</style>
""", unsafe_allow_html=True)


# ============ CARREGAMENTO DE DADOS ============
@st.cache_data
def carregar_vendas(caminho: str, sheet_name: str = 'Vendas') -> pd.DataFrame:
    """Carrega ficheiro de vendas"""
    try:
        if caminho.endswith('.xlsx'):
            try:
                df = pd.read_excel(caminho, sheet_name=sheet_name)
            except:
                # Tentar sem especificar folha
                df = pd.read_excel(caminho)
        elif caminho.endswith('.csv'):
            df = pd.read_csv(caminho)
        else:
            return None
        
        # Converter datas
        for col in df.columns:
            if 'date' in col.lower() or 'data' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar: {str(e)}")
        return None


def classificar_categoria(descricao: str) -> str:
    """Classifica produto em categoria"""
    if pd.isna(descricao):
        return 'Sem Categoria'
    
    desc_lower = str(descricao).lower()
    
    if any(word in desc_lower for word in ['pão', 'broa', 'baguete', 'ciabatta']):
        return 'Pão'
    elif any(word in desc_lower for word in ['pastel', 'bolo', 'tarte', 'croissant', 'donuts']):
        return 'Pastelaria'
    elif any(word in desc_lower for word in ['agua', 'café', 'chá', 'suco', 'sumo', 'bebida', 'leite']):
        return 'Bebidas'
    else:
        return 'Outros'


# ============ VISÃO 1: RESUMO GERAL ============
def visao_ampla(df: pd.DataFrame) -> None:
    """Visão ampla com métricas principais por categoria"""
    st.header("📊 Visão Ampla - por Categoria")
    
    # Adicionar coluna de categoria se não existir
    if 'Categoria' not in df.columns and 'ProductDescription' in df.columns:
        df = df.copy()
        df['Categoria'] = df['ProductDescription'].apply(classificar_categoria)
    
    # KPIs gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Linhas", f"{len(df):,}")
    with col2:
        if 'CreditAmount' in df.columns:
            st.metric("💰 Faturação Total", f"€{df['CreditAmount'].sum():,.2f}")
        else:
            st.metric("💰 Faturação", "N/A")
    with col3:
        if 'CreditAmount' in df.columns:
            st.metric("🎫 Ticket Médio", f"€{df['CreditAmount'].mean():.2f}")
        else:
            st.metric("🎫 Ticket Médio", "N/A")
    with col4:
        if 'ProductDescription' in df.columns:
            st.metric("📦 Produtos Únicos", f"{df['ProductDescription'].nunique()}")
        else:
            st.metric("📦 Produtos", "N/A")
    
    st.divider()
    
    # Resumo por categoria
    st.subheader("📈 Resumo por Categoria")
    
    if 'Categoria' in df.columns:
        resumo_cat = df.groupby('Categoria').agg({
            'Categoria': 'count',
            'CreditAmount': ['sum', 'mean']
        } if 'CreditAmount' in df.columns else {'Categoria': 'count'})
        
        if 'CreditAmount' in df.columns:
            resumo_cat.columns = ['Linhas', 'Faturação (€)', 'Ticket Médio (€)']
            resumo_cat = resumo_cat.sort_values('Faturação (€)', ascending=False)
        else:
            resumo_cat.columns = ['Linhas']
            resumo_cat = resumo_cat.sort_values('Linhas', ascending=False)
        
        # Cards de categoria
        cols = st.columns(len(resumo_cat))
        
        for idx, (categoria, row) in enumerate(resumo_cat.iterrows()):
            with cols[idx]:
                if categoria == 'Pão':
                    card_class = 'card-a'
                    icon = '🍞'
                elif categoria == 'Pastelaria':
                    card_class = 'card-b'
                    icon = '🥐'
                elif categoria == 'Bebidas':
                    card_class = 'card-c'
                    icon = '🥤'
                else:
                    card_class = 'card-c'
                    icon = '📦'
                
                st.markdown(f"""
                <div class="category-card {card_class}">
                    <h3>{icon} {categoria}</h3>
                    <p><b>Linhas:</b> {int(row['Linhas']):,}</p>
                    {f"<p><b>Faturação:</b> €{row['Faturação (€)']:,.2f}</p>" if 'Faturação (€)' in row.index else ""}
                    {f"<p><b>Ticket:</b> €{row['Ticket Médio (€)']:.2f}</p>" if 'Ticket Médio (€)' in row.index else ""}
                </div>
                """, unsafe_allow_html=True)
        
        # Gráfico de distribuição
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            if 'Faturação (€)' in resumo_cat.columns:
                cores = ['#ff6b6b', '#4ecdc4', '#95e1d3', '#ffe0e0']
                resumo_cat['Faturação (€)'].plot(kind='bar', ax=ax, color=cores[:len(resumo_cat)], edgecolor='black')
                ax.set_title("Faturação por Categoria", fontsize=12, fontweight='bold')
                ax.set_ylabel("Faturação (€)")
            else:
                resumo_cat['Linhas'].plot(kind='bar', ax=ax, color='#4ecdc4', edgecolor='black')
                ax.set_title("Linhas por Categoria", fontsize=12, fontweight='bold')
                ax.set_ylabel("Quantidade")
            
            ax.set_xlabel("")
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            fig, ax = plt.subplots(figsize=(10, 6))
            cores = ['#ff6b6b', '#4ecdc4', '#95e1d3', '#ffe0e0']
            if 'Faturação (€)' in resumo_cat.columns:
                ax.pie(resumo_cat['Faturação (€)'], labels=resumo_cat.index, autopct='%1.1f%%',
                       colors=cores[:len(resumo_cat)], startangle=90)
            else:
                ax.pie(resumo_cat['Linhas'], labels=resumo_cat.index, autopct='%1.1f%%',
                       colors=cores[:len(resumo_cat)], startangle=90)
            ax.set_title("Distribuição de Vendas", fontsize=12, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
    
    return df


# ============ VISÃO 2: DRILLDOWN POR CATEGORIA ============
def visao_detalhada(df: pd.DataFrame) -> None:
    """Drilldown interativo por categoria"""
    st.header("🔍 Visão Detalhada - Drilldown por Categoria")
    
    # Adicionar coluna de categoria
    if 'Categoria' not in df.columns and 'ProductDescription' in df.columns:
        df = df.copy()
        df['Categoria'] = df['ProductDescription'].apply(classificar_categoria)
    
    if 'Categoria' not in df.columns:
        st.warning("Coluna de categoria não disponível")
        return
    
    # Tabs para cada categoria
    categorias = sorted(df['Categoria'].unique())
    tabs = st.tabs([f"{cat} ({len(df[df['Categoria']==cat])})" for cat in categorias])
    
    for tab, categoria in zip(tabs, categorias):
        with tab:
            df_cat = df[df['Categoria'] == categoria]
            
            st.subheader(f"📊 Detalhes - {categoria}")
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Linhas", f"{len(df_cat):,}")
            with col2:
                if 'CreditAmount' in df_cat.columns:
                    st.metric("Faturação", f"€{df_cat['CreditAmount'].sum():,.2f}")
            with col3:
                if 'CreditAmount' in df_cat.columns:
                    st.metric("Ticket Médio", f"€{df_cat['CreditAmount'].mean():.2f}")
            with col4:
                if 'ProductDescription' in df_cat.columns:
                    st.metric("Produtos", f"{df_cat['ProductDescription'].nunique()}")
            
            # Dois painéis
            col1, col2 = st.columns(2)
            
            # Painel 1: Top produtos
            with col1:
                st.write("**🏆 Top 10 Produtos**")
                
                if 'ProductDescription' in df_cat.columns and 'CreditAmount' in df_cat.columns:
                    top_prod = df_cat.groupby('ProductDescription')['CreditAmount'].agg(['sum', 'count']).nlargest(10, 'sum')
                    top_prod.columns = ['Faturação', 'Transações']
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    top_prod['Faturação'].plot(kind='barh', ax=ax, color='#2ca02c', edgecolor='black')
                    ax.set_title(f"Top Produtos - {categoria}", fontsize=11, fontweight='bold')
                    ax.set_xlabel("Faturação (€)")
                    ax.grid(True, alpha=0.3, axis='x')
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    st.dataframe(
                        top_prod.style.format({'Faturação': '€{:,.2f}', 'Transações': '{:.0f}'}),
                        use_container_width=True
                    )
            
            # Painel 2: Análise temporal
            with col2:
                st.write("**📅 Análise Temporal**")
                
                if 'InvoiceDate' in df_cat.columns and 'CreditAmount' in df_cat.columns:
                    vendas_dia = df_cat.groupby(df_cat['InvoiceDate'].dt.date)['CreditAmount'].sum()
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(vendas_dia.index, vendas_dia.values, marker='o', linewidth=2, color='#1f77b4')
                    ax.fill_between(range(len(vendas_dia)), vendas_dia.values, alpha=0.3, color='#1f77b4')
                    ax.set_title(f"Faturação Diária - {categoria}", fontsize=11, fontweight='bold')
                    ax.set_xlabel("Data")
                    ax.set_ylabel("Faturação (€)")
                    ax.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Dados de data não disponíveis")
            
            # Tabela completa (expansível)
            with st.expander("📋 Ver todos os dados desta categoria"):
                st.dataframe(
                    df_cat.style.format({
                        col: '€{:,.2f}' for col in df_cat.columns 
                        if 'Amount' in col or 'Price' in col or 'amount' in col
                    }),
                    use_container_width=True,
                    height=400
                )


# ============ VISÃO 3: COMPARAÇÃO ENTRE CATEGORIAS ============
def visao_comparacao(df: pd.DataFrame) -> None:
    """Comparação side-by-side entre categorias"""
    st.header("⚖️ Comparação entre Categorias")
    
    # Adicionar coluna de categoria
    if 'Categoria' not in df.columns and 'ProductDescription' in df.columns:
        df = df.copy()
        df['Categoria'] = df['ProductDescription'].apply(classificar_categoria)
    
    if 'Categoria' not in df.columns:
        st.warning("Coluna de categoria não disponível")
        return
    
    # Seleção de categorias para comparar
    categorias_disponiveis = sorted(df['Categoria'].unique())
    categorias_selecionadas = st.multiselect(
        "Selecionar categorias para comparar",
        options=categorias_disponiveis,
        default=categorias_disponiveis[:2]
    )
    
    if not categorias_selecionadas:
        st.warning("Seleciona pelo menos uma categoria")
        return
    
    st.divider()
    
    # Comparação em gráficos
    if 'CreditAmount' in df.columns and 'ProductDescription' in df.columns:
        col1, col2 = st.columns(2)
        
        # Gráfico 1: Faturação
        with col1:
            comparacao_fat = df[df['Categoria'].isin(categorias_selecionadas)].groupby('Categoria')['CreditAmount'].sum()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            comparacao_fat.plot(kind='bar', ax=ax, color=['#ff6b6b', '#4ecdc4', '#95e1d3', '#ffe0e0'][:len(comparacao_fat)], edgecolor='black')
            ax.set_title("Faturação Total", fontsize=12, fontweight='bold')
            ax.set_ylabel("Faturação (€)")
            ax.set_xlabel("")
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        
        # Gráfico 2: Ticket médio
        with col2:
            comparacao_ticket = df[df['Categoria'].isin(categorias_selecionadas)].groupby('Categoria')['CreditAmount'].mean()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            comparacao_ticket.plot(kind='bar', ax=ax, color=['#ff6b6b', '#4ecdc4', '#95e1d3', '#ffe0e0'][:len(comparacao_ticket)], edgecolor='black')
            ax.set_title("Ticket Médio", fontsize=12, fontweight='bold')
            ax.set_ylabel("Valor (€)")
            ax.set_xlabel("")
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    
    # Tabela comparativa
    if 'CreditAmount' in df.columns:
        tabela_comp = df[df['Categoria'].isin(categorias_selecionadas)].groupby('Categoria').agg({
            'Categoria': 'count',
            'CreditAmount': ['sum', 'mean', 'min', 'max']
        }).round(2)
        
        tabela_comp.columns = ['Linhas', 'Faturação Total (€)', 'Ticket Médio (€)', 'Mínimo (€)', 'Máximo (€)']
        
        st.subheader("📊 Tabela Comparativa")
        st.dataframe(
            tabela_comp.style.format({col: '€{:,.2f}' for col in tabela_comp.columns if 'Mínimo' in col or 'Máximo' in col or '€)' in col}),
            use_container_width=True
        )


# ============ PÁGINA PRINCIPAL ============
def main():
    st.title("📊 Dashboard SAF-T com Drilldown")
    st.markdown("Análise interativa com visão ampla → detalhada por categoria")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Dados")
        
        # Ficheiro padrão
        ficheiro_padrao = 'SAF-T-LIMPO.xlsx'
        
        ficheiros = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.csv'))
        ficheiros = [f.name for f in ficheiros]
        
        if not ficheiros:
            st.error("Nenhum ficheiro encontrado")
            st.stop()
        
        # Colocar ficheiro padrão em primeiro se existir
        if ficheiro_padrao in ficheiros:
            ficheiros.remove(ficheiro_padrao)
            ficheiros = [ficheiro_padrao] + ficheiros
        
        ficheiro_selecionado = st.selectbox("Ficheiro", options=ficheiros, index=0)
        
        # Se é Excel, permitir selecionar folha
        sheet_name = 'Vendas'
        if ficheiro_selecionado.endswith('.xlsx'):
            try:
                excel_file = pd.ExcelFile(ficheiro_selecionado)
                folhas = excel_file.sheet_names
                if len(folhas) > 1:
                    sheet_name = st.selectbox("Folha", options=folhas, index=folhas.index('Vendas') if 'Vendas' in folhas else 0)
            except:
                pass
    
    # Carregar dados
    df = carregar_vendas(ficheiro_selecionado, sheet_name=sheet_name)
    
    if df is None or len(df) == 0:
        st.error("Não consegui carregar os dados")
        st.stop()
    
    # Adicionar categorias
    if 'ProductDescription' in df.columns:
        df['Categoria'] = df['ProductDescription'].apply(classificar_categoria)
    
    # Menu de navegação
    st.sidebar.divider()
    st.sidebar.subheader("🗺️ Navegação")
    
    vista = st.sidebar.radio(
        "Escolher vista",
        options=["📊 Visão Ampla", "🔍 Drilldown", "⚖️ Comparação"],
        index=0
    )
    
    # Exibir vista selecionada
    if vista == "📊 Visão Ampla":
        visao_ampla(df)
    elif vista == "🔍 Drilldown":
        visao_detalhada(df)
    elif vista == "⚖️ Comparação":
        visao_comparacao(df)
    
    # Footer
    st.divider()
    st.markdown(
        f"""
        <div style='text-align: center; color: #888; font-size: 12px;'>
        Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
        Registos: {len(df):,} | Ficheiro: {ficheiro_selecionado} (Folha: {sheet_name})<br>
        Colunas: {', '.join(df.columns[:5])}...
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
