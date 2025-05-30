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
        self.tempos_chegada = self.dados['tempo_de_chegada'].values
        self.tempos_atendimento = self.dados['tempo_atendimento'].values
        self.n = len(self.tempos_chegada)
        self.n = len(self.tempos_chegada)

    def _encontrar_servidor_livre(self):
        for i, tempo_ocupado in enumerate(self.servidores):
            if tempo_ocupado <= 0:
                return i
        return None
        
    def simular(self):
        n = self.n
        NUM_SERVIDORES = self.num_servidores

        self.inicio_atendimento = np.zeros(n)
        self.fim_atendimento = np.zeros(n)
        self.tempo_espera = np.zeros(n)
        fim_servidores = [0.0] * NUM_SERVIDORES
        self.ocupacoes = [[] for _ in range(NUM_SERVIDORES)]

        # Calcular tempos de espera e atendimento corretamente
        for i in range(n):
            chegada = self.tempos_chegada[i]
            duracao = self.tempos_atendimento[i]

            servidor = np.argmin(fim_servidores)
            inicio = max(chegada, fim_servidores[servidor])
            fim = inicio + duracao

            self.inicio_atendimento[i] = inicio
            self.fim_atendimento[i] = fim
            self.tempo_espera[i] = inicio - chegada
            fim_servidores[servidor] = fim

            self.ocupacoes[servidor].append((inicio, duracao, f'Cliente {i+1}'))

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
            'Utilização': rho
        }
    
    def gerar_graficos(self):
        n = len(self.dados)

        # Cores do tema
        cor_primaria = '#00A1E0'    # Azul médico
        cor_secundaria = '#4CAF50'  # Verde saúde
        cor_destaque = '#FF6B6B'    # Vermelho suave
        cor_fundo = '#FFFFFF'       # Branco
        cor_texto = '#2C3E50'       # Azul escuro
        cores_personalizadas = [
            cor_primaria, cor_secundaria, cor_destaque, '#FFA726', '#7E57C2',
            '#26A69A', '#FB8C00', '#5C6BC0', '#66BB6A', '#EC407A'
        ]

        plt.style.use('default')
        plt.rcParams.update({
            'figure.facecolor': cor_fundo,
            'axes.facecolor': cor_fundo,
            'axes.grid': True,
            'grid.alpha': 0.3,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'lines.linewidth': 2.5,
            'font.family': 'sans-serif',
        })

        # Gráfico 1: Tempo de Espera por Cliente
        plt.figure(figsize=(12, 6), facecolor=cor_fundo)
        ax = plt.gca()
        ax.set_facecolor(cor_fundo)
        plt.bar(range(1, n + 1), self.tempo_espera, color=cor_primaria, alpha=0.7)
        plt.title(f"Tempo de Espera por Paciente ({self.num_servidores} Postos)", color=cor_texto)
        plt.xlabel("Paciente", color=cor_texto)
        plt.ylabel("Tempo de Espera (minutos)", color=cor_texto)
        plt.xticks(range(1, n + 1), color=cor_texto)
        plt.yticks(color=cor_texto)
        plt.ylim(0, max(self.tempo_espera) + 1)
        plt.grid(axis='y', linestyle='--', alpha=0.6, color=cor_texto)
        plt.savefig('assets/graphs/tempo_espera.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close()

        # Gráfico 2: Número de Pessoas na Fila ao Longo do Tempo
        timeline = np.linspace(0, self.fim_atendimento.max() + 5, 2000)
        fila = [
            np.sum((self.tempos_chegada <= t) & (self.inicio_atendimento > t)) 
            for t in timeline
        ]
        plt.figure(figsize=(12, 6), facecolor=cor_fundo)
        ax = plt.gca()
        ax.set_facecolor(cor_fundo)
        plt.plot(timeline, fila, label="Pacientes na fila", color=cor_secundaria)
        plt.fill_between(timeline, fila, color=cor_secundaria, alpha=0.2, step="mid")
        plt.title(f"Número de Pacientes na Fila ao Longo do Tempo ({self.num_servidores} Postos)", color=cor_texto)
        plt.xlabel("Tempo (minutos)", color=cor_texto)
        plt.ylabel("Número de Pacientes na Fila", color=cor_texto)
        plt.grid(True, linestyle='--', alpha=0.6, color=cor_texto)
        plt.legend(facecolor=cor_fundo, edgecolor=cor_texto, labelcolor=cor_texto)
        plt.xticks(color=cor_texto)
        plt.yticks(color=cor_texto)
        plt.savefig('assets/graphs/tamanho_fila.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close()

        # Gráfico 3: Ocupação dos Servidores (Gantt)
        fig, ax = plt.subplots(figsize=(14, self.num_servidores * 0.5), facecolor=cor_fundo)        
        ax.set_facecolor(cor_fundo)

        # for servidor, tarefas in enumerate(self.ocupacoes):
        #     for (inicio, duracao, label) in tarefas:
        #         ax.broken_barh([(inicio, duracao)], (servidor * 10, 9),
        #                        facecolors=colors(servidor), edgecolor='black')
        #         ax.text(inicio + duracao / 2, servidor * 10 + 4.5, label,
        #                 ha='center', va='center', fontsize=8)
        
        for servidor, tarefas in enumerate(self.ocupacoes):
            cor = cores_personalizadas[servidor % len(cores_personalizadas)]
            for (inicio, duracao, label) in tarefas:
                ax.broken_barh([(inicio, duracao)], (servidor * 10, 9),
                               facecolors=cor, edgecolor=cor_texto, alpha=0.7)
                ax.text(inicio + duracao / 2, servidor * 10 + 4.5, label,
                        ha='center', va='center', fontsize=8, color=cor_texto, fontweight='bold')

        ax.set_ylim(0, self.num_servidores * 10)
        ax.set_xlim(0, max([inicio + duracao for ocup in self.ocupacoes for (inicio, duracao, _) in ocup]) + 2)
        ax.set_xlabel("Tempo (minutos)", color=cor_texto)
        ax.set_yticks([i * 10 + 4.5 for i in range(self.num_servidores)])
        ax.set_yticklabels([f'Posto {i+1}' for i in range(self.num_servidores)], color=cor_texto)
        ax.set_title("Ocupação dos Postos ao Longo do Tempo", color=cor_texto)
        ax.grid(True, axis='x', linestyle='--', alpha=0.5, color=cor_texto)
        plt.xticks(color=cor_texto)
        plt.yticks(color=cor_texto)
        plt.savefig('assets/graphs/ocupacao_servidores.png', dpi=300, facecolor=cor_fundo, bbox_inches='tight')
        plt.close('all')