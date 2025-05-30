import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class AnalisadorEstatistico:
    def __init__(self, arquivo_dados):
        self.dados = pd.read_csv(arquivo_dados, dtype={
            'tempo_de_chegada': float,
            'tempo_atendimento': float
        })
        
    def calcular_estatisticas_descritivas(self):
        estatisticas = {}
        
        nomes = {
            'tempo_de_chegada': 'Tempo de Chegada:',
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
    
    def gerar_visualizacoes(self):        # Configurar estilo dos gráficos
        plt.style.use('default')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'font.family': 'sans-serif',
        })

        # Cores do tema
        cor_primaria = '#00A1E0'    # Azul médico
        cor_secundaria = '#4CAF50'   # Verde saúde
        cor_destaque = '#FF6B6B'     # Vermelho suave
        cor_fundo = '#FFFFFF'        # Branco
        cor_texto = '#2C3E50'        # Azul escuro
        
        # Criar figura para os histogramas lado a lado
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 6))
        fig.patch.set_facecolor(cor_fundo)
        
        # Histograma do tempo de atendimento
        ax1.set_facecolor(cor_fundo)
        _, bins, _ = ax1.hist(self.dados['tempo_atendimento'], bins=20, color=cor_primaria, alpha=0.7)
        ax1.set_title('Distribuição do Tempo de Atendimento', fontsize=14, color=cor_texto, pad=20)
        ax1.set_xlabel('Tempo (minutos)', fontsize=12, color=cor_texto)
        ax1.set_ylabel('Frequência', fontsize=12, color=cor_texto)
        ax1.grid(True, alpha=0.3, color=cor_texto)
        ax1.tick_params(colors=cor_texto)
        # Forçar valores inteiros no eixo y
        ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        
        # Histograma do tempo de chegada
        ax2.set_facecolor(cor_fundo)
        ax2.hist(self.dados['tempo_de_chegada'], bins=20, color=cor_secundaria, alpha=0.7)
        ax2.set_title('Distribuição do Tempo de Chegada', fontsize=14, color=cor_texto, pad=20)
        ax2.set_xlabel('Tempo (minutos)', fontsize=12, color=cor_texto)
        ax2.set_ylabel('Frequência', fontsize=12, color=cor_texto)
        ax2.grid(True, alpha=0.3, color=cor_texto)
        ax2.tick_params(colors=cor_texto)
        # Forçar valores inteiros no eixo y
        ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

        plt.tight_layout(pad=3.0)
        plt.savefig('assets/graphs/histogramas_estatisticos.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close('all')
        
        # Criar figura separada para o boxplot com estilo semelhante aos histogramas
        plt.figure(figsize=(12, 6))
        fig = plt.gcf()
        fig.patch.set_facecolor(cor_fundo)
        ax = plt.gca()
        ax.set_facecolor(cor_fundo)
        
        box = plt.boxplot(
            [self.dados['tempo_de_chegada'], self.dados['tempo_atendimento']], 
            labels=['Tempo de Chegada', 'Tempo de Atendimento'],
            patch_artist=True,
            boxprops=dict(facecolor=cor_secundaria, color=cor_texto, alpha=0.7),
            whiskerprops=dict(color=cor_texto),
            capprops=dict(color=cor_texto),
            medianprops=dict(color=cor_destaque, linewidth=2),
            flierprops=dict(markerfacecolor=cor_destaque, marker='o', markersize=5, linestyle='none')
        )
        
        plt.title('Comparação dos Tempos', fontsize=14, color=cor_texto, pad=20)
        plt.ylabel('Tempo (min)', fontsize=12, color=cor_texto)
        plt.grid(True, alpha=0.3, color=cor_texto)
        plt.xticks(color=cor_texto)
        plt.yticks(color=cor_texto)

        # Configurar eixo y com intervalos de 1 em 1
        max_valor = max(self.dados['tempo_atendimento'].max(), self.dados['tempo_de_chegada'].max())
        plt.yticks(np.arange(0, max_valor + 1, 1))
        
        plt.tight_layout(pad=3.0)
        plt.savefig('assets/graphs/boxplot_estatistico.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close('all')

    
    def calcular_intervalos_confianca(self, confianca):
        intervalos = {}
        z_critico = stats.norm.ppf((1 + confianca) / 2)
        
        for coluna, nome in {'tempo_de_chegada': 'Tempo de Chegada:', 
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
