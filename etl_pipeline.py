"""
Pipeline ETL Reutilizável para Análise SAF-T
Automatiza o processo de extração, transformação e carregamento de dados
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any


class PipelineETL:
    """Pipeline reutilizável para processamento de ficheiros SAF-T"""
    
    def __init__(self, ficheiro: str):
        """
        Inicializa o pipeline
        
        Args:
            ficheiro: Caminho para o ficheiro Excel a processar
        """
        self.ficheiro = ficheiro
        self.df_original = None
        self.df_processado = None
        self.stats = {}
        self._validar_ficheiro()
    
    def _validar_ficheiro(self) -> None:
        """Valida se o ficheiro existe"""
        if not Path(self.ficheiro).exists():
            raise FileNotFoundError(f"Ficheiro não encontrado: {self.ficheiro}")
    
    # ============ EXTRACT ============
    def extract(self) -> 'PipelineETL':
        """
        Extrai dados do ficheiro Excel
        
        Returns:
            self (para encadeamento de métodos)
        """
        print(f"📥 Extraindo de {Path(self.ficheiro).name}...")
        self.df_original = pd.read_excel(self.ficheiro)
        self.df_processado = self.df_original.copy()
        self.stats['registos_iniciais'] = len(self.df_original)
        self.stats['colunas_iniciais'] = len(self.df_original.columns)
        print(f"   ✓ {self.stats['registos_iniciais']} registos carregados")
        print(f"   ✓ {self.stats['colunas_iniciais']} colunas")
        return self
    
    # ============ TRANSFORM ============
    def remover_prefixos_xml(self) -> 'PipelineETL':
        """
        Remove prefixos XML (ns1:) dos nomes das colunas
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Execute extract() primeiro")
        
        colunas_original = list(self.df_processado.columns)
        self.df_processado.columns = [
            col.replace('ns1:', '') if isinstance(col, str) else col 
            for col in self.df_processado.columns
        ]
        colunas_removidas = sum(1 for col in colunas_original if 'ns1:' in col)
        print(f"✅ Prefixos XML removidos ({colunas_removidas} colunas)")
        return self
    
    def filtrar_vendas_validas(self, 
                               data_coluna: str = 'InvoiceDate',
                               valor_coluna: str = 'CreditAmount') -> 'PipelineETL':
        """
        Filtra apenas linhas com vendas válidas (tem data e valor)
        
        Args:
            data_coluna: Nome da coluna com datas
            valor_coluna: Nome da coluna com valores
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Execute extract() primeiro")
        
        registos_antes = len(self.df_processado)
        self.df_processado = self.df_processado[
            (self.df_processado[data_coluna].notna()) & 
            (self.df_processado[valor_coluna].notna())
        ].copy()
        registos_removidos = registos_antes - len(self.df_processado)
        print(f"✅ Removed {registos_removidos} invalid records")
        print(f"   ✓ Remaining: {len(self.df_processado)} records")
        return self
    
    def converter_tipos(self, tipos_mapa: Optional[Dict[str, str]] = None) -> 'PipelineETL':
        """
        Converte tipos de dados das colunas
        
        Args:
            tipos_mapa: Dicionário com mapeamento {coluna: tipo}
                       Se None, usa conversões padrão para SAF-T
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Execute extract() primeiro")
        
        if tipos_mapa is None:
            # Conversões padrão para SAF-T
            tipos_mapa = {
                'InvoiceDate': 'datetime64[ns]',
                'CreditAmount': 'float64',
                'Quantity': 'float64',
                'UnitPrice': 'float64',
                'TaxPercentage': 'float64'
            }
        
        conversoes_ok = 0
        for coluna, tipo in tipos_mapa.items():
            if coluna in self.df_processado.columns:
                try:
                    if tipo == 'datetime64[ns]':
                        self.df_processado[coluna] = pd.to_datetime(
                            self.df_processado[coluna], 
                            errors='coerce'
                        )
                    elif tipo in ['float64', 'int64']:
                        self.df_processado[coluna] = pd.to_numeric(
                            self.df_processado[coluna], 
                            errors='coerce'
                        )
                    conversoes_ok += 1
                except Exception as e:
                    print(f"   ⚠️ Erro ao converter {coluna}: {str(e)}")
        
        print(f"✅ {conversoes_ok} colunas convertidas com sucesso")
        return self
    
    def remover_duplicados(self, subconjunto: Optional[list] = None) -> 'PipelineETL':
        """
        Remove registos duplicados
        
        Args:
            subconjunto: Lista de colunas para verificar duplicação
                        Se None, verifica todas as colunas
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Execute extract() primeiro")
        
        registos_antes = len(self.df_processado)
        self.df_processado = self.df_processado.drop_duplicates(subset=subconjunto)
        registos_removidos = registos_antes - len(self.df_processado)
        print(f"✅ {registos_removidos} registos duplicados removidos")
        return self
    
    def remover_nulos(self, threshold: float = 0.5) -> 'PipelineETL':
        """
        Remove colunas com muitos valores nulos
        
        Args:
            threshold: Percentagem máxima de nulos permitida (0-1)
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Execute extract() primeiro")
        
        colunas_antes = len(self.df_processado.columns)
        for coluna in self.df_processado.columns:
            pct_nulos = self.df_processado[coluna].isna().sum() / len(self.df_processado)
            if pct_nulos > threshold:
                self.df_processado.drop(coluna, axis=1, inplace=True)
        
        colunas_removidas = colunas_antes - len(self.df_processado.columns)
        print(f"✅ {colunas_removidas} colunas com muitos nulos removidas")
        return self
    
    # ============ LOAD ============
    def exportar_excel(self, caminho_saida: str, index: bool = False) -> 'PipelineETL':
        """
        Exporta dados processados para Excel
        
        Args:
            caminho_saida: Caminho do ficheiro de saída
            index: Se deve incluir índice
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Não há dados para exportar. Execute extract() e transformações.")
        
        self.df_processado.to_excel(caminho_saida, index=index)
        print(f"✅ Dados exportados para {Path(caminho_saida).name}")
        return self
    
    def exportar_csv(self, caminho_saida: str, index: bool = False) -> 'PipelineETL':
        """
        Exporta dados processados para CSV
        
        Args:
            caminho_saida: Caminho do ficheiro de saída
            index: Se deve incluir índice
        
        Returns:
            self (para encadeamento de métodos)
        """
        if self.df_processado is None:
            raise ValueError("Não há dados para exportar. Execute extract() e transformações.")
        
        self.df_processado.to_csv(caminho_saida, index=index, encoding='utf-8')
        print(f"✅ Dados exportados para {Path(caminho_saida).name}")
        return self
    
    # ============ UTILIDADES ============
    def obter_dataframe(self) -> pd.DataFrame:
        """Retorna o DataFrame processado"""
        if self.df_processado is None:
            raise ValueError("Nenhum dado processado ainda")
        return self.df_processado.copy()
    
    def obter_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do processamento"""
        return self.stats.copy()
    
    def relatorio(self) -> None:
        """Imprime relatório de processamento"""
        if not self.stats:
            print("Nenhum processamento realizado ainda")
            return
        
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DO PIPELINE ETL")
        print("=" * 60)
        
        if 'registos_iniciais' in self.stats:
            print(f"\n📈 REGISTOS:")
            print(f"   Iniciais: {self.stats['registos_iniciais']:,}")
            print(f"   Finais: {self.stats['registos_finais']:,}")
            print(f"   Removidos: {self.stats['registos_iniciais'] - self.stats['registos_finais']:,}")
            print(f"   Retenção: {self.stats['retenção']:.1f}%")
        
        if 'colunas_iniciais' in self.stats:
            print(f"\n📋 COLUNAS:")
            print(f"   Iniciais: {self.stats['colunas_iniciais']}")
            if 'colunas_finais' in self.stats:
                print(f"   Finais: {self.stats['colunas_finais']}")
        
        print("\n" + "=" * 60)
    
    # ============ EXECUTAR PIPELINE ============
    def executar(self, incluir_limpeza_completa: bool = False) -> pd.DataFrame:
        """
        Executa o pipeline completo com método fluente
        
        Args:
            incluir_limpeza_completa: Se deve remover duplicados e nulos
        
        Returns:
            DataFrame processado
        """
        self.extract()
        self.remover_prefixos_xml()
        self.filtrar_vendas_validas()
        self.converter_tipos()
        
        if incluir_limpeza_completa:
            self.remover_duplicados()
            self.remover_nulos(threshold=0.7)
        
        # Calcular estatísticas finais
        self.stats['registos_finais'] = len(self.df_processado)
        self.stats['colunas_finais'] = len(self.df_processado.columns)
        self.stats['retenção'] = (
            self.stats['registos_finais'] / self.stats['registos_iniciais'] * 100
        )
        
        self.relatorio()
        
        return self.df_processado


# ============ EXEMPLOS DE USO ============

if __name__ == "__main__":
    # Exemplo 1: Pipeline simples
    print("\n🔧 EXEMPLO 1: Pipeline Simples")
    print("-" * 60)
    
    pipeline = PipelineETL('dados.xlsx')
    df_limpo = (pipeline
        .extract()
        .remover_prefixos_xml()
        .filtrar_vendas_validas()
        .converter_tipos()
        .obter_dataframe()
    )
    
    pipeline.relatorio()
    
    
    # Exemplo 2: Pipeline com limpeza completa e exportação
    print("\n\n🔧 EXEMPLO 2: Pipeline Completo com Exportação")
    print("-" * 60)
    
    pipeline2 = PipelineETL('dados.xlsx')
    (pipeline2
        .extract()
        .remover_prefixos_xml()
        .filtrar_vendas_validas()
        .converter_tipos()
        .remover_duplicados()
        .remover_nulos(threshold=0.7)
        .exportar_excel('dados_limpos.xlsx')
        .relatorio()
    )
    
    
    # Exemplo 3: Acesso aos dados processados
    print("\n\n🔧 EXEMPLO 3: Acesso aos Dados Processados")
    print("-" * 60)
    
    pipeline3 = PipelineETL('dados.xlsx')
    pipeline3.executar(incluir_limpeza_completa=True)
    
    # Obter dados
    df = pipeline3.obter_dataframe()
    stats = pipeline3.obter_stats()
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Estatísticas: {stats}")
