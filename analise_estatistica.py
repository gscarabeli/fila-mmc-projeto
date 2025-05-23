import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class AnalisadorEstatistico:
    def __init__(self, arquivo_dados):
        # Converter as colunas para float ao ler o CSV
        self.dados = pd.read_csv(arquivo_dados, dtype={
            'tempo_entre_chegadas': float,
            'tempo_atendimento': float
        })
        
    def calcular_estatisticas_descritivas(self):
        estatisticas = {}
        
        nomes = {
            'tempo_entre_chegadas': 'Tempo entre chegadas:',
            'tempo_atendimento': 'Tempo de atendimento:'
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
            estatisticas[nome] = {
                metricas['media']: dados.mean(),
                metricas['mediana']: dados.median(),
                metricas['moda']: dados.mode().iloc[0],
                metricas['variancia']: dados.var(),
                metricas['desvio_padrao']: dados.std()
            }
            
        return estatisticas
    
    def gerar_visualizacoes(self):
        # Configurar estilo dark mode
        plt.style.use('dark_background')
        plt.figure(figsize=(20, 8))
        
        # Histograma do tempo de atendimento
        plt.subplot(121)
        plt.hist(self.dados['tempo_atendimento'], bins=20, color='#3498db', alpha=0.7)
        plt.title('Distribuição do Tempo de Atendimento:', fontsize=14, color='white')
        plt.xlabel('Tempo (min)', fontsize=12, color='white')
        plt.ylabel('Frequência', fontsize=12, color='white')
        plt.grid(True, alpha=0.2)
        
        # Boxplot comparativo
        plt.subplot(122)
        plt.boxplot([self.dados['tempo_atendimento'], self.dados['tempo_entre_chegadas']], 
                   labels=['Tempo de Atendimento:', 'Tempo entre Chegadas:'],
                   patch_artist=True,
                   boxprops=dict(facecolor='#2ecc71', color='white', alpha=0.7),
                   whiskerprops=dict(color='white'),
                   capprops=dict(color='white'),
                   medianprops=dict(color='white'))
        plt.title('Comparação dos Tempos:', fontsize=14, color='white')
        plt.ylabel('Tempo (min)', fontsize=12, color='white')
        plt.grid(True, alpha=0.2)
        
        plt.tight_layout(pad=3.0)
        plt.savefig('assets/graficos_estatisticos.png', dpi=300, facecolor='#1a1a1a')
        plt.close()
    
    def calcular_intervalos_confianca(self, confianca=0.95):
        intervalos = {}
        
        nomes = {
            'tempo_entre_chegadas': 'Tempo entre chegadas:',
            'tempo_atendimento': 'Tempo de atendimento:'
        }
        
        for coluna, nome in nomes.items():
            dados = self.dados[coluna]
            media = dados.mean()
            erro_padrao = stats.sem(dados)
            ic = stats.t.interval(confianca, len(dados)-1, media, erro_padrao)
            
            intervalos[nome] = {
                'inferior': ic[0],
                'superior': ic[1]
            }
            
        return intervalos