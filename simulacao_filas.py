import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import math  # Adicionando importação do math

class SimuladorFilas:
    def __init__(self, num_servidores, arquivo_dados):
        self.num_servidores = num_servidores
        # Converter as colunas para float ao ler o CSV
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
        """
        Encontra o primeiro servidor disponível.
        Retorna o índice do servidor livre ou None se não houver servidores disponíveis.
        """
        for i, tempo_ocupado in enumerate(self.servidores):
            if tempo_ocupado <= 0:
                return i
        return None
    def simular(self):
        tempo_atual = 0
        tempo_eventos = []  # Lista para controlar eventos de saída
        
        for _, cliente in self.dados.iterrows():
            # Atualizar tempo
            tempo_atual += cliente['tempo_entre_chegadas']
            
            # Processar saídas antes da nova chegada
            for i, tempo_saida in enumerate(self.servidores):
                if tempo_saida > 0 and tempo_saida <= tempo_atual:
                    self.servidores[i] = 0
                    # Se há alguém na fila, atender próximo cliente
                    if self.fila:
                        cliente_fila = self.fila.popleft()
                        tempo_espera = tempo_atual - cliente_fila['chegada']
                        self.historico_espera.append(tempo_espera)
                        self.servidores[i] = tempo_atual + cliente_fila['tempo_atendimento']
            
            # Verificar servidores disponíveis para novo cliente
            servidor_livre = self._encontrar_servidor_livre()
            
            if servidor_livre is not None:
                self.servidores[servidor_livre] = tempo_atual + cliente['tempo_atendimento']
                self.historico_espera.append(0)
            else:
                self.fila.append({
                    'chegada': tempo_atual,
                    'tempo_atendimento': cliente['tempo_atendimento']
                })
            
            # Registrar estado do sistema
            self.historico_fila.append(len(self.fila))
            self.historico_ocupacao.append(sum([1 for s in self.servidores if s > tempo_atual]))
    
    def _calcular_p0(self, lambda_taxa, mu_taxa):
        """
        Calcula a probabilidade do sistema estar vazio (P0)
        """
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        c = self.num_servidores
        
        # Primeira parte da soma
        soma = sum([(c * rho)**n / math.factorial(n) for n in range(c-1)])
        
        # Segunda parte
        ultima_parte = (c * rho)**c / (math.factorial(c) * (1 - rho))
        
        # P0 é o inverso da soma total
        return 1 / (soma + ultima_parte)
    
    def _calcular_p_espera(self, lambda_taxa, mu_taxa):
        """
        Calcula a probabilidade de espera na fila
        """
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        c = self.num_servidores
        p0 = self._calcular_p0(lambda_taxa, mu_taxa)
        
        return (lambda_taxa**c * p0) / (math.factorial(c) * mu_taxa**c * (1 - rho))
    
    def _calcular_lq(self, lambda_taxa, mu_taxa):
        """
        Calcula o número médio de clientes na fila
        """
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        p_espera = self._calcular_p_espera(lambda_taxa, mu_taxa)
        
        return (rho * p_espera) / (1 - rho)
    
    def calcular_metricas(self):
        lambda_taxa = 1 / self.dados['tempo_entre_chegadas'].mean()
        mu_taxa = 1 / self.dados['tempo_atendimento'].mean()
        rho = lambda_taxa / (self.num_servidores * mu_taxa)
        
        # Cálculo das métricas do sistema M/M/c
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
        # Configurar estilo dark mode
        plt.style.use('dark_background')
        
        # Calcular dados necessários para os gráficos
        n = len(self.dados)
        tempos_chegada = np.zeros(n)
        tempo_atual = 0
        for i, cliente in enumerate(self.dados.itertuples()):
            tempo_atual += cliente.tempo_entre_chegadas
            tempos_chegada[i] = tempo_atual

        # Inicialização para simulação
        inicio_atendimento = np.zeros(n)
        fim_atendimento = np.zeros(n)
        fim_servidores = [0.0] * self.num_servidores
        tempo_espera = np.zeros(n)
        ocupacoes = {i: [] for i in range(self.num_servidores)}

        # Simulação do atendimento
        for i in range(n):
            chegada = tempos_chegada[i]
            duracao = self.dados.iloc[i]['tempo_atendimento']

            # Encontrar servidor mais livre
            servidor = min(range(self.num_servidores), key=lambda x: fim_servidores[x])
            inicio = max(chegada, fim_servidores[servidor])
            fim = inicio + duracao
            
            # Registrar dados
            inicio_atendimento[i] = inicio
            fim_atendimento[i] = fim
            tempo_espera[i] = inicio - chegada
            ocupacoes[servidor].append((inicio, duracao, i+1))
            fim_servidores[servidor] = fim

        # Configurar subplots
        plt.figure(figsize=(20, 8))

        # 1. Gráfico de tempo de espera por cliente
        plt.subplot(131)
        plt.bar(range(1, n+1), tempo_espera, color='#2ecc71', edgecolor='white', alpha=0.7)
        media_espera = np.mean(tempo_espera)
        plt.axhline(y=media_espera, color='white', linestyle='--', alpha=0.5,
                   label=f'Média: {media_espera:.1f} min')
        plt.title('Tempo de Espera por Cliente', fontsize=14, color='white')
        plt.xlabel('Cliente', fontsize=12, color='white')
        plt.ylabel('Tempo (min)', fontsize=12, color='white')
        plt.grid(True, alpha=0.2)
        plt.legend()
        plt.ylim(bottom=0)        # 2. Gráfico de tamanho da fila ao longo do tempo
        plt.subplot(132)
        
        # Recalcular inicio_atendimento e fim_atendimento
        inicio_atendimento = np.zeros(n)
        fim_atendimento = np.zeros(n)
        fim_servidores = [0.0] * self.num_servidores

        # Simular atendimento com o número correto de servidores
        for i in range(n):
            chegada = tempos_chegada[i]
            duracao = self.dados.iloc[i]['tempo_atendimento']
            
            # Encontrar servidor mais livre
            servidor = min(range(self.num_servidores), key=lambda x: fim_servidores[x])
            inicio = max(chegada, fim_servidores[servidor])
            fim = inicio + duracao
            
            inicio_atendimento[i] = inicio
            fim_atendimento[i] = fim
            fim_servidores[servidor] = fim

        # Criar linha do tempo para o gráfico
        timeline = np.linspace(0, max(fim_atendimento) + 5, 2000)
        fila_size = [np.sum((tempos_chegada <= t) & (inicio_atendimento > t)) for t in timeline]

        plt.plot(timeline, fila_size, color='#3498db', label='Pessoas na fila')
        media_fila = np.mean(fila_size)
        plt.axhline(y=media_fila, color='white', linestyle='--', alpha=0.5,
                   label=f'Média: {media_fila:.1f} pessoas')
        plt.title('Número de Pessoas na Fila ao Longo do Tempo', fontsize=14, color='white')
        plt.xlabel('Tempo (minutos)', fontsize=12, color='white')
        plt.ylabel('Número de Pessoas na Fila', fontsize=12, color='white')
        plt.grid(True, alpha=0.2)
        plt.legend()
        plt.ylim(bottom=0)

        # 3. Gráfico de ocupação dos servidores (Gantt)
        plt.subplot(133)
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#c0392b']
        ax = plt.gca()
        for servidor, tarefas in ocupacoes.items():
            for (inicio, duracao, label) in tarefas:
                ax.broken_barh([(inicio, duracao)], 
                             (servidor * 10, 9),
                             facecolors=colors[servidor % len(colors)],
                             edgecolor='white',
                             alpha=0.7)
                # Adicionar o número do cliente no centro da barra
                ax.text(inicio + duracao/2, servidor * 10 + 4.5, label,
                       ha='center', va='center', color='white',
                       fontsize=8)

        plt.title('Ocupação dos Servidores', fontsize=14, color='white')
        plt.xlabel('Tempo (min)', fontsize=12, color='white')
        plt.yticks([5 + 10*i for i in range(self.num_servidores)],
                  [f'Servidor {i+1}' for i in range(self.num_servidores)])
        plt.grid(True, alpha=0.2)
        plt.ylim(0, 10 * self.num_servidores + 5)

        # Ajustar layout e salvar
        plt.tight_layout(pad=3.0)
        plt.savefig('assets/graficos_simulacao.png', dpi=300, facecolor='#1a1a1a', bbox_inches='tight')
        plt.close('all')