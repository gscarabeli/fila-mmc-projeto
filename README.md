# 🧮 Simulação de Filas M/M/c - Projeto Interdisciplinar

## 🎯 Objetivo

Desenvolver uma aplicação em Python para simular o comportamento de um sistema de filas com múltiplos servidores (modelo M/M/c), utilizando dados simulados e reais. O sistema foi projetado para analisar desempenho, prever gargalos e apoiar decisões operacionais em contextos como clínicas, restaurantes ou centrais de suporte.

Este projeto é interdisciplinar, integrando conhecimentos de:

- Engenharia de Software
- Estatística
- Pesquisa Operacional


## 🚀 Como Executar

### Pré-requisitos:
- Python 3.10+
- Bibliotecas:
  - pandas
  - matplotlib
  - numpy
  - seaborn
  - scipy
  - flask

### Passos:
1. Clone o repositório ou extraia os arquivos.
2. Instale as dependências (caso tenha `requirements.txt`):
   ```bash
   pip install -r requirements.txt
  (ou instale manualmente os pacotes utilizados)
3. Para rodar o sistema:
4. Acesse a interface local pelo navegador: http://localhost:5000

## 📁 Estrutura do Projeto

Simulador Fila MMc/
│
├── main.py                    # Script principal para iniciar a aplicação
├── simulacao_filas.py         # Lógica de simulação M/M/c
├── analise_estatistica.py     # Cálculos e gráficos estatísticos
├── templates/                 # Templates HTML da interface
├── static/                    # Arquivos CSS e imagens
└── assets/                    # Arquivos auxiliares e dados


## 👥 Equipe

| Nome Completo                    | Papel / Responsabilidades                        |
|----------------------------------|--------------------------------------------------|
| Artur Rossi Junior               | Simulação, integração Flask, interface           |
| Gustavo Correa Pedro de Carvalho | Cálculos estatísticos e métricas                 |
| Gustavo Correia Scarabeli        | Gráficos, visualizações, documentação            |
| Matheus Andrade de Oliveira      | Organização do projeto, relatórios finais        |


## 📊 Tarefas por disciplina

### 🛠 Engenharia de Software
- Definição de papéis do Scrum (PO, SM, Dev Team)
- Criação do Product Backlog com 10+ tarefas
- Planejamento por Sprint (1 a 3)
- Organização visual com Kanban no Trello
- Participação nas cerimônias Scrum simuladas
- Relatório com evidências do processo de desenvolvimento
- Estrutura e documentação do projeto

### 🔢 Pesquisa Operacional
- Leitura e uso de dados simulados de chegada e atendimento
- Simulação do sistema de filas M/M/c com múltiplos servidores
- Cálculo das métricas de desempenho do sistema:
  - P₀: Probabilidade do sistema vazio
  - P<sub>espera</sub>: Probabilidade de espera
  - L<sub>q</sub>, W<sub>q</sub>, L, W
- Geração de gráficos para:
  - Tempo de espera por cliente
  - Tamanho da fila ao longo do tempo
  - Ocupação dos servidores
- Análise de cenários: adicionar servidor ou aumentar μ

### 📈 Estatística
- Cálculo de medidas descritivas:
  - Média, mediana, moda, variância, desvio padrão
- Visualização dos dados:
  - Histogramas dos tempos de atendimento e espera
  - Boxplot comparando tempos de atendimento vs espera
- Inferência estatística:
  - Intervalos de confiança para as médias dos tempos
- Interpretação dos dados e recomendações baseadas nas análises


## 📌 Observações

Este projeto foi desenvolvido como parte da avaliação interdisciplinar do 2º bimestre do curso, integrando as disciplinas de Engenharia de Software, Estatística e Pesquisa Operacional.

A aplicação simula o comportamento de filas com múltiplos servidores (modelo M/M/c) utilizando dados reais ou simulados. Também realiza análises estatísticas e oferece visualizações úteis para avaliação de desempenho do sistema.

O código está modularizado, com separação entre simulação, análise estatística e interface. O projeto está preparado para futuras expansões, como:

- Integração com dashboard via Streamlit
- Análise de sensibilidade com diferentes parâmetros
- Uso de dados reais de empresas parceiras

