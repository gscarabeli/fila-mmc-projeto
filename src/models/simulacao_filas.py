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

        plt.style.use('dark_background')
        n = len(self.dados)

        # Primeiro gráfico - Tempo de espera por cliente
        tempos_espera_ordenados = sorted(self.historico_espera)
        plt.figure(figsize=(12, 6))
        plt.bar(range(1, n+1), tempos_espera_ordenados, color='orange', edgecolor='black')
        plt.title("Tempo de Espera por Cliente")
        plt.xlabel("Cliente")
        plt.ylabel("Tempo de Espera (minutos)")
        plt.xticks(range(1, n+1))
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig('assets/tempo_espera.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close()

        # Segundo gráfico - Número de pessoas na fila (esperando, para qualquer número de servidores)
        plt.figure(figsize=(12, 6))
        
        # Pegar todos os tempos de eventos (chegadas e saídas do atendimento)
        eventos_tempo = np.sort(np.concatenate([self.tempos_chegada, self.fim_atendimento]))
        fila = [max(0, np.sum((self.tempos_chegada <= t) & (self.fim_atendimento > t)) - self.num_servidores) for t in eventos_tempo]
        
        plt.step(eventos_tempo, fila, where='post', color='blue', linewidth=2, label='Pessoas na fila')
        plt.title(f'Número de Pessoas na Fila ao Longo do Tempo ({self.num_servidores} servidores)')
        plt.xlabel('Tempo (minutos)')
        plt.ylabel('Número de pessoas na fila (esperando)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim(0, max(fila) + 1)
        plt.xlim(0, max(eventos_tempo))
        plt.tight_layout()
        plt.savefig('assets/tamanho_fila.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close()

        # Terceiro gráfico - Ocupação dos servidores
        plt.figure(figsize=(12, 6))
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#c0392b']
        ax = plt.gca()

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
                ax.broken_barh([(inicio, duracao)], 
                             (servidor * 10, 9),
                             facecolors=colors[servidor],
                             edgecolor='white',
                             alpha=0.7)
                ax.text(inicio + duracao/2, servidor * 10 + 4.5, str(label),
                       ha='center', va='center', color='white',
                       fontsize=8)

        plt.title('Ocupação dos Servidores', fontsize=14, color='white')
        plt.xlabel('Tempo (min)', fontsize=12, color='white')
        plt.yticks([5 + 10*i for i in range(self.num_servidores)],
                  [f'Servidor {i+1}' for i in range(self.num_servidores)])
        plt.grid(True, alpha=0.2)
        plt.ylim(0, 10 * self.num_servidores + 5)
        plt.tight_layout()
        plt.savefig('assets/ocupacao_servidores.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close('all')