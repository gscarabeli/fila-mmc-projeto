import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import math  # Adicionando importacao do math

class SimuladorFilas:
    def __init__(self, num_servidores, arquivo_dados):
        self.num_servidores = num_servidores
        self.dados = pd.read_csv(arquivo_dados, dtype={
            'tempo_de_chegada': float,
            'tempo_atendimento': float
        })
        self.fila = deque()
        self.servidores = [0] * num_servidores
        self.historico_fila = []
        self.historico_espera = []
        self.historico_ocupacao = []

    def _encontrar_servidor_livre(self):
        for i, tempo_ocupado in enumerate(self.servidores):
            if tempo_ocupado <= 0:
                return i
        return None
        
    def simular(self):
        # Calcular tempos reais de chegada
        self.dados['tempo_chegada'] = self.dados['tempo_de_chegada'].cumsum()
        
        # Inicializar variáveis
        n = len(self.dados)
        self.servidores = [0] * self.num_servidores
        self.historico_espera = []
        self.historico_ocupacao = []
        tempo_total_espera = 0
        
        # Arrays para armazenar os tempos
        self.inicio_atendimento = np.zeros(n)
        self.fim_atendimento = np.zeros(n)
        self.tempos_chegada = self.dados['tempo_chegada'].values
        self.tempos_atendimento = self.dados['tempo_atendimento'].values
        fim_servidores = [0] * self.num_servidores
        
        # Lista para armazenar eventos (chegada: +1, saída: -1)
        eventos = []
        
        for i in range(n):
            chegada = self.tempos_chegada[i]
            duracao = self.tempos_atendimento[i]
            
            # Encontrar servidor que ficará livre primeiro
            servidor_idx = min(range(self.num_servidores), key=lambda x: fim_servidores[x])
            inicio = max(chegada, fim_servidores[servidor_idx])
            fim = inicio + duracao
            
            # Registrar eventos de chegada e saída
            eventos.append((chegada, 1))           # Chegada
            eventos.append((inicio + duracao, -1)) # Saída
            
            # Armazenar tempos
            self.inicio_atendimento[i] = inicio
            self.fim_atendimento[i] = fim
            fim_servidores[servidor_idx] = fim
            
            # Calcular e acumular tempo de espera
            tempo_espera = inicio - chegada
            tempo_total_espera += tempo_espera
            self.historico_espera.append(tempo_total_espera)
        
        # Ordenar eventos por tempo
        eventos.sort()
        
        # Criar timeline e calcular tamanho da fila
        self.timeline = []
        self.fila = []
        pessoas_na_fila = 0
        
        for tempo, mudanca in eventos:
            self.timeline.append(tempo)
            pessoas_na_fila += mudanca
            self.fila.append(max(0, pessoas_na_fila - self.num_servidores))

    def _calcular_p0(self, lambda_taxa, mu_taxa):
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        c = self.num_servidores
        soma = sum([(c * rho)**n / math.factorial(n) for n in range(c-1)])
        ultima_parte = (c * rho)**c / (math.factorial(c) * (1 - rho))
        return 1 / (soma + ultima_parte)

    def _calcular_p_espera(self, lambda_taxa, mu_taxa):
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        c = self.num_servidores
        p0 = self._calcular_p0(lambda_taxa, mu_taxa)
        return (lambda_taxa**c * p0) / (math.factorial(c) * mu_taxa**c * (1 - rho))

    def _calcular_lq(self, lambda_taxa, mu_taxa):
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        p_espera = self._calcular_p_espera(lambda_taxa, mu_taxa)
        return (rho * p_espera) / (1 - rho)

    def calcular_metricas(self):
        lambda_taxa = 1 / self.dados['tempo_de_chegada'].mean()
        mu_taxa = 1 / self.dados['tempo_atendimento'].mean()
        rho = lambda_taxa / (self.num_servidores * mu_taxa)

        p0 = self._calcular_p0(lambda_taxa, mu_taxa)
        p_espera = self._calcular_p_espera(lambda_taxa, mu_taxa)
        lq = self._calcular_lq(lambda_taxa, mu_taxa)
        wq = lq / lambda_taxa
        l = lq + (lambda_taxa / mu_taxa)
        w = wq + (1 / mu_taxa)

        return {
            'P0': p0,
            'P_espera': p_espera,
            'Lq': lq,
            'Wq': wq,
            'L': l,
            'W': w,
            'Utilizacao': rho
        }
    
    def gerar_graficos(self):
        if not hasattr(self, 'timeline'):
            self.simular()

        # Configuração do estilo dos gráficos
        plt.style.use('default')
        # Configurações gerais do matplotlib
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.grid': True,
            'grid.alpha': 0.3,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'lines.linewidth': 2.5,
            'font.family': 'sans-serif',
        })
        n = len(self.dados)

        # Cores do tema
        cor_primaria = '#00A1E0'    # Azul médico
        cor_secundaria = '#4CAF50'   # Verde saúde
        cor_destaque = '#FF6B6B'     # Vermelho suave
        cor_fundo = '#FFFFFF'        # Branco
        cor_texto = '#2C3E50'        # Azul escuro

        # Primeiro gráfico - Tempo de espera por cliente
        tempos_espera_ordenados = sorted(self.historico_espera)
        plt.figure(figsize=(12, 6), facecolor=cor_fundo)
        ax = plt.gca()
        ax.set_facecolor(cor_fundo)
        plt.bar(range(1, n+1), tempos_espera_ordenados, color=cor_primaria, alpha=0.7)
        plt.title("Tempo de Espera por Paciente", color=cor_texto, fontsize=14, pad=20)
        plt.xlabel("Paciente", color=cor_texto, fontsize=12)
        plt.ylabel("Tempo de Espera (minutos)", color=cor_texto, fontsize=12)
        plt.xticks(range(1, n+1), color=cor_texto)
        plt.yticks(color=cor_texto)
        plt.grid(axis='y', linestyle='--', alpha=0.3, color=cor_texto)
        plt.tight_layout()
        plt.savefig('assets/graphs/tempo_espera.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close()

        # Segundo gráfico - Número de pessoas na fila (esperando, para qualquer número de servidores)
        plt.figure(figsize=(12, 6), facecolor=cor_fundo)
        ax = plt.gca()
        ax.set_facecolor(cor_fundo)
        
        # Pegar todos os tempos de eventos (chegadas e saídas do atendimento)
        eventos_tempo = np.sort(np.concatenate([self.tempos_chegada, self.fim_atendimento]))
        fila = [max(0, np.sum((self.tempos_chegada <= t) & (self.fim_atendimento > t)) - self.num_servidores) for t in eventos_tempo]
        
        plt.step(eventos_tempo, fila, where='post', color=cor_secundaria, linewidth=2.5, label='Pacientes aguardando')
        plt.fill_between(eventos_tempo, fila, step="post", alpha=0.2, color=cor_secundaria)
        plt.title(f'Tamanho da Fila ao Longo do Tempo ({self.num_servidores} postos)', color=cor_texto, fontsize=14, pad=20)
        plt.xlabel('Tempo (minutos)', color=cor_texto, fontsize=12)
        plt.ylabel('Número de pacientes aguardando', color=cor_texto, fontsize=12)
        plt.grid(True, alpha=0.3, color=cor_texto)
        plt.legend(facecolor=cor_fundo, edgecolor=cor_texto, labelcolor=cor_texto)
        plt.ylim(0, max(fila) + 1)
        plt.xlim(0, max(eventos_tempo))
        plt.xticks(color=cor_texto)
        plt.yticks(color=cor_texto)
        plt.tight_layout()
        plt.savefig('assets/graphs/tamanho_fila.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close()        # Terceiro gráfico - Ocupação dos servidores
        plt.figure(figsize=(12, 6), facecolor=cor_fundo)
        colors = [cor_primaria, cor_secundaria, '#FF6B6B', '#FFA726', '#7E57C2', '#26A69A', '#FB8C00', '#5C6BC0', '#66BB6A', '#EC407A']
        ax = plt.gca()
        ax.set_facecolor(cor_fundo)

        tempo_atual = 0
        fim_servidores = [0] * self.num_servidores
        ocupacoes = {i: [] for i in range(self.num_servidores)}

        for i, cliente in enumerate(self.dados.itertuples()):
            tempo_atual += float(cliente.tempo_de_chegada)
            duracao = float(cliente.tempo_atendimento)

            if self.historico_espera[i] == 0:
                servidor = min(range(self.num_servidores), key=lambda x: fim_servidores[x])
                inicio = tempo_atual
            else:
                servidor = min(range(self.num_servidores), key=lambda x: fim_servidores[x])
                inicio = fim_servidores[servidor]

            fim_servidores[servidor] = inicio + duracao
            ocupacoes[servidor].append((inicio, duracao, i+1))

        for servidor, tarefas in ocupacoes.items():
            for inicio, duracao, label in tarefas:
                ax.broken_barh([(inicio, duracao)], (servidor * 10, 9), facecolors=colors[servidor],edgecolor=cor_texto, alpha=0.7)
                ax.text(inicio + duracao/2, servidor * 10 + 4.5, str(label), ha='center', va='center', color=cor_texto, fontsize=8, fontweight='bold')

        plt.title('Ocupação dos Postos de Vacinação', fontsize=14, color=cor_texto, pad=20)
        plt.xlabel('Tempo (minutos)', fontsize=12, color=cor_texto)
        plt.yticks([5 + 10*i for i in range(self.num_servidores)], [f'Posto {i+1}' for i in range(self.num_servidores)], color=cor_texto)
        plt.xticks(color=cor_texto)
        plt.grid(True, alpha=0.2, color=cor_texto)
        plt.ylim(0, 10 * self.num_servidores + 5)
        plt.tight_layout()
        plt.savefig('assets/graphs/ocupacao_servidores.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close('all')