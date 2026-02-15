"""
Testes de Qualidade de Dados para SAF-T
Valida, estrutura e integridade dos dados processados
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestResult:
    """Resultado de um teste de qualidade"""
    nome: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    mensagem: str
    detalhes: Optional[Dict] = None


class TestesQualidadeDados:
    """Suite de testes para validação de qualidade de dados"""
    
    def __init__(self, df: pd.DataFrame, nome_dataset: str = "Dataset"):
        """
        Inicializa testes de qualidade
        
        Args:
            df: DataFrame a validar
            nome_dataset: Nome do dataset para relatórios
        """
        self.df = df
        self.nome_dataset = nome_dataset
        self.resultados = []
        self.timestamp = datetime.now()
    
    # ============ TESTES DE COMPLETUDE ============
    def testar_completude(self, coluna: str, max_nulos_pct: float = 5.0) -> TestResult:
        """
        Valida quantidade de valores nulos numa coluna
        
        Args:
            coluna: Nome da coluna
            max_nulos_pct: Máximo de nulos permitido em %
        
        Returns:
            TestResult com resultado do teste
        """
        if coluna not in self.df.columns:
            resultado = TestResult(
                nome=f"Completude: {coluna}",
                status="FAIL",
                mensagem=f"Coluna '{coluna}' não existe",
                detalhes={"colunas_validas": list(self.df.columns)}
            )
        else:
            nulos = self.df[coluna].isna().sum()
            pct_nulos = (nulos / len(self.df)) * 100
            
            if pct_nulos <= max_nulos_pct:
                status = "PASS"
                mensagem = f"✅ {coluna}: {pct_nulos:.2f}% nulos (aceitável)"
            else:
                status = "FAIL"
                mensagem = f"❌ {coluna}: {pct_nulos:.2f}% nulos (limite: {max_nulos_pct}%)"
            
            resultado = TestResult(
                nome=f"Completude: {coluna}",
                status=status,
                mensagem=mensagem,
                detalhes={"nulos": int(nulos), "pct_nulos": round(pct_nulos, 2)}
            )
        
        self.resultados.append(resultado)
        return resultado
    
    def testar_completude_multiplas(self, colunas: List[str], max_nulos_pct: float = 5.0) -> List[TestResult]:
        """Testa completude de múltiplas colunas"""
        return [self.testar_completude(col, max_nulos_pct) for col in colunas]
    
    # ============ TESTES DE CONSISTÊNCIA ============
    def testar_tipo_dados(self, coluna: str, tipo_esperado: str) -> TestResult:
        """
        Valida tipo de dados de uma coluna
        
        Args:
            coluna: Nome da coluna
            tipo_esperado: Tipo esperado (datetime64, float64, int64, object, etc.)
        
        Returns:
            TestResult com resultado do teste
        """
        if coluna not in self.df.columns:
            resultado = TestResult(
                nome=f"Tipo Dados: {coluna}",
                status="FAIL",
                mensagem=f"Coluna '{coluna}' não existe"
            )
        else:
            tipo_atual = str(self.df[coluna].dtype)
            if tipo_atual == tipo_esperado:
                status = "PASS"
                mensagem = f"✅ {coluna}: tipo '{tipo_esperado}' correto"
            else:
                status = "FAIL"
                mensagem = f"❌ {coluna}: tipo '{tipo_atual}' (esperado: '{tipo_esperado}')"
            
            resultado = TestResult(
                nome=f"Tipo Dados: {coluna}",
                status=status,
                mensagem=mensagem,
                detalhes={"tipo_atual": tipo_atual, "tipo_esperado": tipo_esperado}
            )
        
        self.resultados.append(resultado)
        return resultado
    
    def testar_intervalo(self, coluna: str, min_valor: float = None, max_valor: float = None) -> TestResult:
        """
        Valida se valores estão dentro de um intervalo
        
        Args:
            coluna: Nome da coluna
            min_valor: Valor mínimo permitido
            max_valor: Valor máximo permitido
        
        Returns:
            TestResult com resultado do teste
        """
        if coluna not in self.df.columns:
            resultado = TestResult(
                nome=f"Intervalo: {coluna}",
                status="FAIL",
                mensagem=f"Coluna '{coluna}' não existe"
            )
        else:
            col_limpa = self.df[coluna].dropna()
            
            violacoes = 0
            if min_valor is not None:
                violacoes += (col_limpa < min_valor).sum()
            if max_valor is not None:
                violacoes += (col_limpa > max_valor).sum()
            
            if violacoes == 0:
                status = "PASS"
                mensagem = f"✅ {coluna}: todos valores dentro intervalo [{min_valor}, {max_valor}]"
            else:
                status = "FAIL"
                mensagem = f"❌ {coluna}: {violacoes} valores fora do intervalo [{min_valor}, {max_valor}]"
            
            resultado = TestResult(
                nome=f"Intervalo: {coluna}",
                status=status,
                mensagem=mensagem,
                detalhes={
                    "min_valor": float(col_limpa.min()) if len(col_limpa) > 0 else None,
                    "max_valor": float(col_limpa.max()) if len(col_limpa) > 0 else None,
                    "violacoes": int(violacoes)
                }
            )
        
        self.resultados.append(resultado)
        return resultado
    
    # ============ TESTES DE INTEGRIDADE ============
    def testar_duplicados(self, colunas: List[str], permitir_alguns: bool = False) -> TestResult:
        """
        Valida se há registos duplicados
        
        Args:
            colunas: Colunas para verificar duplicação
            permitir_alguns: Se True, avisa mas não falha
        
        Returns:
            TestResult com resultado do teste
        """
        duplicados = self.df.duplicated(subset=colunas).sum()
        
        if duplicados == 0:
            status = "PASS"
            mensagem = f"✅ Sem registos duplicados em {colunas}"
        else:
            status = "WARNING" if permitir_alguns else "FAIL"
            mensagem = f"{'⚠️' if permitir_alguns else '❌'} {duplicados} registos duplicados encontrados"
        
        resultado = TestResult(
            nome=f"Duplicados: {colunas}",
            status=status,
            mensagem=mensagem,
            detalhes={"duplicados": int(duplicados), "percentagem": round((duplicados/len(self.df))*100, 2)}
        )
        
        self.resultados.append(resultado)
        return resultado
    
    def testar_chave_primaria(self, colunas: List[str]) -> TestResult:
        """
        Valida se colunas formam chave primária (valores únicos)
        
        Args:
            colunas: Colunas que devem ser únicas
        
        Returns:
            TestResult com resultado do teste
        """
        unicos = len(self.df[colunas].drop_duplicates())
        total = len(self.df)
        
        if unicos == total:
            status = "PASS"
            mensagem = f"✅ Chave primária válida em {colunas}"
        else:
            status = "FAIL"
            mensagem = f"❌ {total - unicos} combinações duplicadas em {colunas}"
        
        resultado = TestResult(
            nome=f"Chave Primária: {colunas}",
            status=status,
            mensagem=mensagem,
            detalhes={"unicos": int(unicos), "total": int(total)}
        )
        
        self.resultados.append(resultado)
        return resultado
    
    # ============ TESTES DE CONFORMIDADE ============
    def testar_valores_positivos(self, coluna: str) -> TestResult:
        """
        Valida se todos valores são positivos
        
        Args:
            coluna: Nome da coluna
        
        Returns:
            TestResult com resultado do teste
        """
        if coluna not in self.df.columns:
            resultado = TestResult(
                nome=f"Positivos: {coluna}",
                status="FAIL",
                mensagem=f"Coluna '{coluna}' não existe"
            )
        else:
            col_limpa = self.df[coluna].dropna()
            negativos = (col_limpa < 0).sum()
            
            if negativos == 0:
                status = "PASS"
                mensagem = f"✅ {coluna}: todos valores positivos"
            else:
                status = "FAIL"
                mensagem = f"❌ {coluna}: {negativos} valores negativos encontrados"
            
            resultado = TestResult(
                nome=f"Positivos: {coluna}",
                status=status,
                mensagem=mensagem,
                detalhes={"negativos": int(negativos)}
            )
        
        self.resultados.append(resultado)
        return resultado
    
    def testar_datas_validas(self, coluna: str) -> TestResult:
        """
        Valida se coluna contém datas válidas
        
        Args:
            coluna: Nome da coluna
        
        Returns:
            TestResult com resultado do teste
        """
        if coluna not in self.df.columns:
            resultado = TestResult(
                nome=f"Datas Válidas: {coluna}",
                status="FAIL",
                mensagem=f"Coluna '{coluna}' não existe"
            )
        else:
            try:
                col_limpa = self.df[coluna].dropna()
                # Verifica se é datetime
                if pd.api.types.is_datetime64_any_dtype(col_limpa):
                    status = "PASS"
                    mensagem = f"✅ {coluna}: datas válidas"
                    detalhes = {
                        "data_minima": str(col_limpa.min()),
                        "data_maxima": str(col_limpa.max())
                    }
                else:
                    status = "FAIL"
                    mensagem = f"❌ {coluna}: não é tipo datetime"
                    detalhes = {}
            except Exception as e:
                status = "FAIL"
                mensagem = f"❌ {coluna}: erro ao validar datas - {str(e)}"
                detalhes = {}
            
            resultado = TestResult(
                nome=f"Datas Válidas: {coluna}",
                status=status,
                mensagem=mensagem,
                detalhes=detalhes
            )
        
        self.resultados.append(resultado)
        return resultado
    
    # ============ TESTES CUSTOMIZADOS ============
    def testar_condicao_customizada(self, nome: str, condicao: pd.Series, 
                                   mensagem_sucesso: str = "Teste passou",
                                   mensagem_erro: str = "Teste falhou") -> TestResult:
        """
        Executa teste customizado baseado em condição
        
        Args:
            nome: Nome do teste
            condicao: Series booleana True=passa, False=falha
            mensagem_sucesso: Mensagem se passar
            mensagem_erro: Mensagem se falhar
        
        Returns:
            TestResult com resultado do teste
        """
        falhas = (~condicao).sum()
        
        if falhas == 0:
            status = "PASS"
            mensagem = f"✅ {mensagem_sucesso}"
        else:
            status = "FAIL"
            mensagem = f"❌ {mensagem_erro} ({falhas} registos)"
        
        resultado = TestResult(
            nome=nome,
            status=status,
            mensagem=mensagem,
            detalhes={"falhas": int(falhas)}
        )
        
        self.resultados.append(resultado)
        return resultado
    
    # ============ TESTES DE NEGÓCIO ============
    def testar_faturacao_consistente(self, coluna_valor: str, coluna_qtd: str, coluna_preco: str) -> TestResult:
        """
        Valida se faturação = quantidade × preço
        
        Args:
            coluna_valor: Coluna com valores totais
            coluna_qtd: Coluna com quantidades
            coluna_preco: Coluna com preços unitários
        
        Returns:
            TestResult com resultado do teste
        """
        try:
            df_valido = self.df[[coluna_valor, coluna_qtd, coluna_preco]].dropna()
            
            # Calcular faturação esperada
            fat_calculada = df_valido[coluna_qtd] * df_valido[coluna_preco]
            
            # Permitir pequena margem de erro (0.01)
            inconsistencias = (abs(df_valido[coluna_valor] - fat_calculada) > 0.01).sum()
            
            if inconsistencias == 0:
                status = "PASS"
                mensagem = f"✅ Faturação consistente (qtd × preço)"
            else:
                status = "FAIL"
                mensagem = f"❌ {inconsistencias} linhas com faturação inconsistente"
            
            resultado = TestResult(
                nome="Faturação Consistente",
                status=status,
                mensagem=mensagem,
                detalhes={"inconsistencias": int(inconsistencias)}
            )
        except Exception as e:
            resultado = TestResult(
                nome="Faturação Consistente",
                status="FAIL",
                mensagem=f"❌ Erro ao validar: {str(e)}"
            )
        
        self.resultados.append(resultado)
        return resultado
    
    # ============ RELATÓRIOS ============
    def gerar_relatorio(self, verbose: bool = True) -> Dict:
        """
        Gera relatório completo dos testes
        
        Args:
            verbose: Se True, imprime relatório
        
        Returns:
            Dicionário com resumo dos testes
        """
        if not self.resultados:
            return {"erro": "Nenhum teste executado"}
        
        resumo = {
            "dataset": self.nome_dataset,
            "timestamp": self.timestamp.isoformat(),
            "registos": len(self.df),
            "colunas": len(self.df.columns),
            "testes": {
                "total": len(self.resultados),
                "passou": sum(1 for r in self.resultados if r.status == "PASS"),
                "falhou": sum(1 for r in self.resultados if r.status == "FAIL"),
                "aviso": sum(1 for r in self.resultados if r.status == "WARNING")
            },
            "taxa_sucesso": round(
                (sum(1 for r in self.resultados if r.status == "PASS") / len(self.resultados) * 100),
                2
            ),
            "resultados": [
                {
                    "nome": r.nome,
                    "status": r.status,
                    "mensagem": r.mensagem,
                    "detalhes": r.detalhes
                }
                for r in self.resultados
            ]
        }
        
        if verbose:
            self._imprimir_relatorio(resumo)
        
        return resumo
    
    def _imprimir_relatorio(self, resumo: Dict) -> None:
        """Imprime relatório formatado"""
        print("\n" + "=" * 80)
        print(f"📋 RELATÓRIO DE QUALIDADE DE DADOS - {resumo['dataset']}")
        print("=" * 80)
        
        print(f"\n📊 INFORMAÇÕES DO DATASET:")
        print(f"   Registos: {resumo['registos']:,}")
        print(f"   Colunas: {resumo['colunas']}")
        
        print(f"\n🧪 RESUMO DOS TESTES:")
        print(f"   Total: {resumo['testes']['total']}")
        print(f"   ✅ Passou: {resumo['testes']['passou']}")
        print(f"   ❌ Falhou: {resumo['testes']['falhou']}")
        print(f"   ⚠️ Aviso: {resumo['testes']['aviso']}")
        print(f"   Taxa de Sucesso: {resumo['taxa_sucesso']}%")
        
        print(f"\n📝 DETALHES DOS TESTES:")
        print("-" * 80)
        
        for resultado in resumo['resultados']:
            print(f"\n{resultado['mensagem']}")
            if resultado['detalhes']:
                for chave, valor in resultado['detalhes'].items():
                    print(f"   • {chave}: {valor}")
        
        print("\n" + "=" * 80)
    
    def exportar_relatorio_json(self, caminho: str) -> None:
        """Exporta relatório em JSON"""
        import json
        
        resumo = self.gerar_relatorio(verbose=False)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(resumo, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatório exportado para {caminho}")


# ============ EXEMPLO DE USO ============

if __name__ == "__main__":
    # Carregar dados
    df = pd.read_excel('dados_limpos.xlsx')
    
    # Criar tester
    tester = TestesQualidadeDados(df, nome_dataset="SAF-T Processado")
    
    # Executar testes
    print("\n🔍 EXECUTANDO TESTES DE QUALIDADE...\n")
    
    # Testes de completude
    tester.testar_completude('InvoiceDate', max_nulos_pct=1.0)
    tester.testar_completude('CreditAmount', max_nulos_pct=1.0)
    
    # Testes de tipo de dados
    tester.testar_tipo_dados('InvoiceDate', 'datetime64[ns]')
    tester.testar_tipo_dados('CreditAmount', 'float64')
    
    # Testes de intervalo
    tester.testar_intervalo('CreditAmount', min_valor=0)
    
    # Testes de duplicados
    tester.testar_duplicados(['InvoiceDate', 'ProductCode'])
    
    # Testes de valores positivos
    tester.testar_valores_positivos('CreditAmount')
    
    # Testes de datas
    tester.testar_datas_validas('InvoiceDate')
    
    # Gerar relatório
    relatorio = tester.gerar_relatorio(verbose=True)
    
    # Exportar
    tester.exportar_relatorio_json('relatorio_qualidade.json')
