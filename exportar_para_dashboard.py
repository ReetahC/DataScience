"""
Script para exportar dados de vendas do notebook para Excel
Cria ficheiro 'vendas.xlsx' compatível com o dashboard
"""

import pandas as pd
import json
from pathlib import Path


def extrair_dados_notebook():
    """
    Extrai dados de vendas do notebook e cria ficheiro Excel
    
    Procura por variáveis do kernel do notebook e exporta:
    - vendas_por_data (completo com InvoiceDate, CreditAmount, etc.)
    - ou vendas_por_mes
    - ou dados brutos df_analise
    """
    
    print("📁 Extrator de Dados - Notebook → Excel\n")
    print("=" * 60)
    
    # Verificar se o notebook existe
    notebook_path = Path('analise_saft_rita_costa.ipynb')
    
    if not notebook_path.exists():
        print("❌ Notebook não encontrado: analise_saft_rita_costa.ipynb")
        print("\n💡 Alternativa: Cria ficheiro vendas.xlsx manualmente com colunas:")
        print("   - InvoiceDate")
        print("   - ProductDescription")
        print("   - CreditAmount")
        print("   - Quantity (opcional)")
        return False
    
    print(f"✅ Notebook encontrado: {notebook_path}\n")
    
    # Ler o notebook
    try:
        import nbformat
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)
        
        print("📖 Notebook carregado")
        print(f"   Células: {len(nb.cells)}")
        
        # Procurar por código Python que crie dataframes
        variaveis_encontradas = []
        
        for i, cell in enumerate(nb.cells):
            if cell.cell_type == 'code':
                if any(var in cell.source for var in ['vendas_por_data', 'df_analise', 'vendas_por_mes']):
                    variaveis_encontradas.append((i, cell.source[:100]))
        
        if variaveis_encontradas:
            print(f"\n✅ Encontrei {len(variaveis_encontradas)} células relevantes")
            for idx, snippet in variaveis_encontradas:
                print(f"   Célula {idx}: {snippet.replace(chr(10), ' ')[:50]}...")
        else:
            print("\n⚠️ Não encontrei variáveis de vendas no notebook")
        
        return True
        
    except ImportError:
        print("⚠️ nbformat não instalado")
        print("   pip install nbformat")
        return False
    except Exception as e:
        print(f"❌ Erro ao ler notebook: {e}")
        return False


def criar_vendas_exemplo():
    """
    Cria ficheiro vendas.xlsx de exemplo para testes
    """
    print("\n📝 Criando ficheiro de exemplo: vendas.xlsx\n")
    
    import numpy as np
    from datetime import datetime, timedelta
    
    # Gerar dados exemplo
    datas = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    produtos = [
        'Pão de Trigo', 'Pão de Milho', 'Pão Integral', 'Baguete',
        'Pastel de Nata', 'Croissant', 'Tarte de Maçã', 'Bolo de Chocolate',
        'Café Expresso', 'Água', 'Sumo de Laranja', 'Chá',
        'Manteiga', 'Queijo', 'Presunto'
    ]
    
    def categorizar(prod):
        if any(x in prod for x in ['Pão', 'Baguete']):
            return 'Pão'
        elif any(x in prod for x in ['Pastel', 'Croissant', 'Tarte', 'Bolo']):
            return 'Pastelaria'
        elif any(x in prod for x in ['Café', 'Água', 'Sumo', 'Chá']):
            return 'Bebidas'
        else:
            return 'Outros'
    
    # Gerar registos
    np.random.seed(42)
    n_registos = 5000
    
    dados = {
        'InvoiceDate': np.random.choice(datas, n_registos),
        'ProductDescription': np.random.choice(produtos, n_registos),
        'Quantity': np.random.randint(1, 10, n_registos),
        'UnitPrice': np.random.uniform(0.5, 15, n_registos).round(2),
    }
    
    df = pd.DataFrame(dados)
    df['CreditAmount'] = (df['Quantity'] * df['UnitPrice']).round(2)
    df['Categoria'] = df['ProductDescription'].apply(categorizar)
    
    # Ordenar por data
    df = df.sort_values('InvoiceDate').reset_index(drop=True)
    
    # Exportar
    ficheiro_saida = 'vendas.xlsx'
    df.to_excel(ficheiro_saida, index=False, sheet_name='Vendas')
    
    print(f"✅ Ficheiro criado: {ficheiro_saida}")
    print(f"   Registos: {len(df):,}")
    print(f"   Colunas: {', '.join(df.columns)}")
    print(f"   Período: {df['InvoiceDate'].min().date()} a {df['InvoiceDate'].max().date()}")
    print(f"   Faturação: €{df['CreditAmount'].sum():,.2f}")
    
    return ficheiro_saida


def main():
    print("\n" + "🔧" * 30)
    print("EXPORTADOR: Notebook → Excel para Dashboard")
    print("🔧" * 30 + "\n")
    
    # Tentar extrair do notebook
    sucesso = extrair_dados_notebook()
    
    if not sucesso:
        print("\n❓ Deseja criar dataset de exemplo?")
        resposta = input("Escreve 'sim' para continuar: ").strip().lower()
        
        if resposta == 'sim':
            criar_vendas_exemplo()
            print("\n✅ Agora podes executar:")
            print("   streamlit run dashboard_drilldown.py")
        else:
            print("\n💡 Para criar manualmente:")
            print("   1. Abre o Excel")
            print("   2. Cria as colunas: InvoiceDate, ProductDescription, CreditAmount")
            print("   3. Salva como vendas.xlsx")
            print("   4. Coloca na mesma pasta do dashboard")
    else:
        print("\n✅ Para exportar dados do notebook:")
        print("   1. Abre o notebook em VS Code")
        print("   2. Executa todas as células")
        print("   3. Adiciona uma célula nova:")
        print("")
        print("      # Exportar para Excel")
        print("      df_analise.to_excel('vendas.xlsx', index=False)")
        print("")
        print("   4. Depois executa o dashboard:")
        print("      streamlit run dashboard_drilldown.py")


if __name__ == "__main__":
    main()
