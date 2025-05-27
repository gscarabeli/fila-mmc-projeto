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
            'tempo_entre_chegadas': float,
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
        tempo_atual = 0
        self.historico_fila = []
        self.historico_espera = []
        self.historico_ocupacao = []
        self.historico_tempos = []
        self.fila = deque()
        self.servidores = [0] * self.num_servidores

        for _, cliente in self.dados.iterrows():
            tempo_atual += cliente['tempo_entre_chegadas']

            for i, tempo_saida in enumerate(self.servidores):
                if tempo_saida > 0 and tempo_saida <= tempo_atual:
                    self.servidores[i] = 0
                    if self.fila:
                        cliente_fila = self.fila.popleft()
                        self.servidores[i] = tempo_atual + cliente_fila['tempo_atendimento']

            servidor_livre = self._encontrar_servidor_livre()

            if servidor_livre is not None:
                self.servidores[servidor_livre] = tempo_atual + cliente['tempo_atendimento']
                self.historico_espera.append(0)
            else:
                self.fila.append({
                    'chegada': tempo_atual,
                    'tempo_atendimento': cliente['tempo_atendimento']
                })
                proximo_livre = min(self.servidores)
                tempo_espera = proximo_livre - tempo_atual
                self.historico_espera.append(tempo_espera)

            self.historico_fila.append(len(self.fila))
            self.historico_tempos.append(tempo_atual)
            self.historico_ocupacao.append(sum([1 for s in self.servidores if s > tempo_atual]))

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
        lambda_taxa = 1 / self.dados['tempo_entre_chegadas'].mean()
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
        if not self.historico_fila:
            self.simular()

        plt.style.use('dark_background')
        n = len(self.dados)
        plt.figure(figsize=(20, 8))

        plt.subplot(131)
        plt.bar(range(1, n+1), self.historico_espera, color='#2ecc71', edgecolor='white', alpha=0.7)
        plt.title('Tempo de Espera por Cliente', fontsize=14, color='white')
        plt.xlabel('Cliente', fontsize=12, color='white')
        plt.ylabel('Tempo de Espera (minutos)', fontsize=12, color='white')
        plt.grid(axis='y', alpha=0.2, linestyle='--')
        plt.xticks(range(1, n+1))
        plt.ylim(bottom=0)

        plt.subplot(132)
        plt.step(self.historico_tempos, self.historico_fila, where='post', 
                color='blue', linewidth=2, label='Pessoas na fila')
        plt.title('Numero de Pessoas na Fila ao Longo do Tempo (2 servidores)', 
                 fontsize=14, color='white')
        plt.xlabel('Tempo (minutos)', fontsize=12, color='white')
        plt.ylabel('Numero de Pessoas na Fila', fontsize=12, color='white')
        plt.grid(True, alpha=0.2)
        plt.legend(framealpha=0.8)
        plt.ylim(bottom=0)
        max_pessoas = max(self.historico_fila)
        plt.ylim(0, max_pessoas + 1)

        plt.subplot(133)
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#c0392b']
        ax = plt.gca()

        tempo_atual = 0
        fim_servidores = [0] * self.num_servidores
        ocupacoes = {i: [] for i in range(self.num_servidores)}

        for i, cliente in enumerate(self.dados.itertuples()):
            tempo_atual += cliente.tempo_entre_chegadas
            duracao = cliente.tempo_atendimento

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

        plt.title('Ocupacao dos Servidores', fontsize=14, color='white')
        plt.xlabel('Tempo (min)', fontsize=12, color='white')
        plt.yticks([5 + 10*i for i in range(self.num_servidores)],
                  [f'Servidor {i+1}' for i in range(self.num_servidores)])
        plt.grid(True, alpha=0.2)
        plt.ylim(0, 10 * self.num_servidores + 5)

        plt.tight_layout(pad=3.0)
        plt.savefig('assets/graficos_simulacao.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close('all')