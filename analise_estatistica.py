import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class AnalisadorEstatistico:
    def __init__(self, arquivo_dados):
        self.dados = pd.read_csv(arquivo_dados, dtype={
            'tempo_entre_chegadas': float,
            'tempo_atendimento': float
        })
        
    def calcular_estatisticas_descritivas(self):
        estatisticas = {}
        
        nomes = {
            'tempo_entre_chegadas': 'Tempo entre Chegadas:',
            'tempo_atendimento': 'Tempo de Atendimento:'
        }
        
        metricas = {
            'media': 'Média',
            'mediana': 'Mediana',
            'moda': 'Moda',
            'variancia': 'Variância',
            'desvio_padrao': 'Desvio Padrão'
        }
        
        for coluna, nome in nomes.items():
            dados = self.dados[coluna]
            moda = dados.mode()
            valor_moda = "Não possui moda" if len(moda) > 1 else moda.iloc[0]
            
            estatisticas[nome] = {
                metricas['media']: dados.mean(),
                metricas['mediana']: dados.median(),
                metricas['moda']: valor_moda,
                metricas['variancia']: dados.var(),
                metricas['desvio_padrao']: dados.std()
            }
            
        return estatisticas
    
    def gerar_visualizacoes(self):
        # Configurar estilo dark mode para todos os gráficos
        plt.style.use('dark_background')
        
        # Criar figura para os histogramas lado a lado
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))
        
        # Histograma do tempo de atendimento
        _, bins, _ = ax1.hist(self.dados['tempo_atendimento'], bins=20, color='#3498db', alpha=0.7)
        ax1.set_title('Distribuição do Tempo de Atendimento', fontsize=14, color='white')
        ax1.set_xlabel('Tempo (min)', fontsize=12, color='white')
        ax1.set_ylabel('Frequência', fontsize=12, color='white')
        ax1.grid(True, alpha=0.2)
        # Forçar valores inteiros no eixo y
        ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        # Histograma do tempo entre chegadas
        ax2.hist(self.dados['tempo_entre_chegadas'], bins=20, color='#e74c3c', alpha=0.7)
        ax2.set_title('Distribuição do Tempo entre Chegadas', fontsize=14, color='white')
        ax2.set_xlabel('Tempo (min)', fontsize=12, color='white')
        ax2.set_ylabel('Frequência', fontsize=12, color='white')
        ax2.grid(True, alpha=0.2)
        # Forçar valores inteiros no eixo y
        ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout(pad=3.0)
        # Ensure the directory exists and clean up any existing file
        plt.savefig('assets/histogramas_estatisticos.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close('all')
        
        # Criar figura separada para o boxplot
        plt.figure(figsize=(12, 6))
        plt.boxplot([self.dados['tempo_entre_chegadas'], self.dados['tempo_atendimento']], 
                   labels=['Tempo entre Chegadas', 'Tempo de Atendimento'],
                   patch_artist=True,
                   boxprops=dict(facecolor='#2ecc71', color='white', alpha=0.7),
                   whiskerprops=dict(color='white'),
                   capprops=dict(color='white'),
                   medianprops=dict(color='white'))
        plt.title('Comparação dos Tempos', fontsize=14, color='white')
        plt.ylabel('Tempo (min)', fontsize=12, color='white')
        plt.grid(True, alpha=0.2)
        
        # Configurar eixo y com intervalos de 1 em 1
        max_valor = max(self.dados['tempo_atendimento'].max(), self.dados['tempo_entre_chegadas'].max())
        plt.yticks(np.arange(0, max_valor + 1, 1))
        
        plt.tight_layout(pad=3.0)
        fig = plt.gcf()
        plt.savefig('assets/boxplot_estatistico.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close('all')
    
    def calcular_intervalos_confianca(self, confianca):
        intervalos = {}
        z_critico = stats.norm.ppf((1 + confianca) / 2)
        
        for coluna, nome in {'tempo_entre_chegadas': 'Tempo entre Chegadas:', 
                            'tempo_atendimento': 'Tempo de Atendimento:'}.items():
            dados = self.dados[coluna]
            media = dados.mean()
            erro_padrao = dados.std() / np.sqrt(len(dados))
            margem_erro = z_critico * erro_padrao
            
            intervalos[nome] = {
                'inferior': media - margem_erro,
                'superior': media + margem_erro
            }
        
        return intervalos
