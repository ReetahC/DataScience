"""
Pipeline Completo: ETL + Testes de Qualidade
Integra limpeza de dados com validação automática
"""

from etl_pipeline import PipelineETL
from data_quality_tests import TestesQualidadeDados
from pathlib import Path
import json


class PipelineComQualidade:
    """Pipeline ETL com validação automática de qualidade"""
    
    def __init__(self, ficheiro_entrada: str):
        """
        Inicializa pipeline com validação
        
        Args:
            ficheiro_entrada: Caminho do ficheiro a processar
        """
        self.ficheiro_entrada = ficheiro_entrada
        self.pipeline_etl = None
        self.tester = None
        self.df_processado = None
        self.resultados = {}
    
    def executar_etl(self, incluir_limpeza_completa: bool = False) -> 'PipelineComQualidade':
        """
        Executa o pipeline ETL
        
        Args:
            incluir_limpeza_completa: Se deve fazer limpeza avançada
        
        Returns:
            self (para encadeamento)
        """
        print("\n" + "=" * 80)
        print("🚀 INICIANDO PIPELINE COMPLETO")
        print("=" * 80)
        
        self.pipeline_etl = PipelineETL(self.ficheiro_entrada)
        self.df_processado = self.pipeline_etl.executar(
            incluir_limpeza_completa=incluir_limpeza_completa
        )
        
        self.resultados['etl'] = self.pipeline_etl.obter_stats()
        return self
    
    def executar_testes_qualidade(self) -> 'PipelineComQualidade':
        """
        Executa testes de qualidade automáticos
        
        Returns:
            self (para encadeamento)
        """
        if self.df_processado is None:
            raise ValueError("Execute executar_etl() primeiro")
        
        print("\n" + "=" * 80)
        print("🧪 INICIANDO TESTES DE QUALIDADE")
        print("=" * 80)
        
        self.tester = TestesQualidadeDados(self.df_processado, "SAF-T Processado")
        
        # Testes padrão para SAF-T
        self._executar_testes_padrao()
        
        self.resultados['qualidade'] = self.tester.gerar_relatorio(verbose=True)
        return self
    
    def _executar_testes_padrao(self) -> None:
        """Executa suite padrão de testes"""
        
        print("\n📋 TESTES PADRÃO SAF-T:\n")
        
        # Identificar colunas existentes
        colunas = self.df_processado.columns
        
        # Testes de completude
        if 'InvoiceDate' in colunas:
            self.tester.testar_completude('InvoiceDate', max_nulos_pct=1.0)
        
        if 'CreditAmount' in colunas:
            self.tester.testar_completude('CreditAmount', max_nulos_pct=1.0)
        
        if 'ProductCode' in colunas:
            self.tester.testar_completude('ProductCode', max_nulos_pct=2.0)
        
        if 'Quantity' in colunas:
            self.tester.testar_completude('Quantity', max_nulos_pct=2.0)
        
        # Testes de tipo de dados
        if 'InvoiceDate' in colunas:
            self.tester.testar_tipo_dados('InvoiceDate', 'datetime64[ns]')
        
        if 'CreditAmount' in colunas:
            self.tester.testar_tipo_dados('CreditAmount', 'float64')
        
        if 'Quantity' in colunas:
            self.tester.testar_tipo_dados('Quantity', 'float64')
        
        if 'UnitPrice' in colunas:
            self.tester.testar_tipo_dados('UnitPrice', 'float64')
        
        # Testes de intervalo
        if 'CreditAmount' in colunas:
            self.tester.testar_intervalo('CreditAmount', min_valor=0)
        
        if 'Quantity' in colunas:
            self.tester.testar_intervalo('Quantity', min_valor=0)
        
        if 'UnitPrice' in colunas:
            self.tester.testar_intervalo('UnitPrice', min_valor=0)
        
        if 'TaxPercentage' in colunas:
            self.tester.testar_intervalo('TaxPercentage', min_valor=0, max_valor=100)
        
        # Testes de duplicados
        if 'InvoiceDate' in colunas and 'ProductCode' in colunas:
            self.tester.testar_duplicados(['InvoiceDate', 'ProductCode'], permitir_alguns=True)
        
        # Testes de valores positivos
        if 'CreditAmount' in colunas:
            self.tester.testar_valores_positivos('CreditAmount')
        
        if 'Quantity' in colunas:
            self.tester.testar_valores_positivos('Quantity')
        
        # Testes de datas
        if 'InvoiceDate' in colunas:
            self.tester.testar_datas_validas('InvoiceDate')
    
    def exportar_dados(self, caminho_saida: str, formato: str = 'excel') -> 'PipelineComQualidade':
        """
        Exporta dados processados
        
        Args:
            caminho_saida: Caminho do ficheiro de saída
            formato: 'excel' ou 'csv'
        
        Returns:
            self (para encadeamento)
        """
        if self.pipeline_etl is None:
            raise ValueError("Execute executar_etl() primeiro")
        
        if formato == 'excel':
            self.pipeline_etl.exportar_excel(caminho_saida)
        elif formato == 'csv':
            self.pipeline_etl.exportar_csv(caminho_saida)
        else:
            raise ValueError(f"Formato '{formato}' não suportado")
        
        return self
    
    def exportar_relatorios(self, pasta_saida: str = '.') -> 'PipelineComQualidade':
        """
        Exporta relatórios (ETL e Qualidade)
        
        Args:
            pasta_saida: Pasta para guardar relatórios
        
        Returns:
            self (para encadeamento)
        """
        pasta = Path(pasta_saida)
        pasta.mkdir(parents=True, exist_ok=True)
        
        # Exportar relatório de qualidade
        if self.tester:
            rel_qualidade = pasta / "relatorio_qualidade.json"
            self.tester.exportar_relatorio_json(str(rel_qualidade))
        
        # Exportar resumo do pipeline
        resumo = {
            "etl": self.resultados.get('etl', {}),
            "qualidade": self.resultados.get('qualidade', {})
        }
        
        rel_pipeline = pasta / "relatorio_pipeline.json"
        with open(rel_pipeline, 'w', encoding='utf-8') as f:
            json.dump(resumo, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatórios exportados para {pasta_saida}/")
        return self
    
    def gerar_resumo(self) -> Dict:
        """
        Gera resumo completo do processamento
        
        Returns:
            Dicionário com resumo
        """
        return {
            "ficheiro_entrada": self.ficheiro_entrada,
            "etl": self.resultados.get('etl', {}),
            "qualidade": self.resultados.get('qualidade', {})
        }


# ============ SCRIPT DE EXECUÇÃO ============

def processar_saft(ficheiro_entrada: str, 
                   ficheiro_saida: str = 'dados_limpos.xlsx',
                   pasta_relatorios: str = 'relatorios') -> None:
    """
    Função de conveniência para processar ficheiro SAF-T completo
    
    Args:
        ficheiro_entrada: Caminho do ficheiro original
        ficheiro_saida: Caminho do ficheiro processado
        pasta_relatorios: Pasta para guardar relatórios
    """
    print("\n" + "🔧" * 40)
    print("PIPELINE COMPLETO: ETL + QUALIDADE DE DADOS")
    print("🔧" * 40)
    
    # Criar e executar pipeline
    pipeline = (PipelineComQualidade(ficheiro_entrada)
        .executar_etl(incluir_limpeza_completa=True)
        .executar_testes_qualidade()
        .exportar_dados(ficheiro_saida, formato='excel')
        .exportar_relatorios(pasta_relatorios)
    )
    
    # Imprimir resumo final
    resumo = pipeline.gerar_resumo()
    
    print("\n" + "=" * 80)
    print("📊 RESUMO FINAL DO PROCESSAMENTO")
    print("=" * 80)
    
    etl = resumo.get('etl', {})
    qualidade = resumo.get('qualidade', {})
    
    print(f"\n📈 ETL:")
    print(f"   Registos iniciais: {etl.get('registos_iniciais', 'N/A'):,}")
    print(f"   Registos finais: {etl.get('registos_finais', 'N/A'):,}")
    print(f"   Retenção: {etl.get('retenção', 'N/A')}%")
    
    print(f"\n✅ QUALIDADE DE DADOS:")
    testes = qualidade.get('testes', {})
    print(f"   Testes executados: {testes.get('total', 'N/A')}")
    print(f"   Passou: {testes.get('passou', 'N/A')}")
    print(f"   Falhou: {testes.get('falhou', 'N/A')}")
    print(f"   Taxa de sucesso: {qualidade.get('taxa_sucesso', 'N/A')}%")
    
    print(f"\n📁 FICHEIROS GERADOS:")
    print(f"   Dados limpos: {ficheiro_saida}")
    print(f"   Relatórios: ./{pasta_relatorios}/")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Exemplo: Processar ficheiro SAF-T
    processar_saft(
        ficheiro_entrada='dados.xlsx',
        ficheiro_saida='dados_limpos.xlsx',
        pasta_relatorios='relatorios_qualidade'
    )
