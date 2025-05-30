from models.simulacao_filas import SimuladorFilas
from services.analise_estatistica import AnalisadorEstatistico
from flask import Flask, render_template, jsonify, send_from_directory, request, send_file
import pandas as pd
import os
from datetime import datetime

# Configura o Flask para encontrar os diretórios corretamente
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

def generate_results_csv(metricas, estatisticas, intervalos_confianca):
    # Configura o caminho para a pasta assets
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
    
    # Definição dos rótulos das métricas em português
    metricas_labels = {
        'P0': 'Probabilidade Sistema Vazio (P0)',
        'P_espera': 'Probabilidade de Espera',
        'Lq': 'Número Médio na Fila (Lq)',
        'Wq': 'Tempo Médio na Fila (Wq)',
        'L': 'Número Médio no Sistema (L)',
        'W': 'Tempo Médio no Sistema (W)',
        'Utilização': 'Taxa de Utilização'
    }
    metricas_dict = {metricas_labels.get(k, k): [v] for k, v in metricas.items()}
    
    # Preparação das estatísticas descritivas
    estatisticas_dict = {}
    medidas_labels = {
        'Média': 'Média',
        'Mediana': 'Mediana',
        'Moda': 'Moda',
        'Variância': 'Variância',
        'Desvio Padrão': 'Desvio Padrão'
    }
    for tipo, valores in estatisticas.items():
        tipo_clean = tipo.replace(':', '')
        for metrica, valor in valores.items():
            col_name = f"{tipo_clean} - {medidas_labels.get(metrica, metrica)}"
            estatisticas_dict[col_name] = [valor]
    
    # Preparação dos intervalos de confiança
    intervalos_dict = {}
    for tipo, valores in intervalos_confianca.items():
        tipo_clean = tipo.replace(':', '')
        for limite, valor in valores.items():
            label = 'Limite Inferior' if limite == 'inferior' else 'Limite Superior'
            col_name = f"{tipo_clean} - {label}"
            intervalos_dict[col_name] = [valor]
    
    # Combina todos os dados e gera o CSV
    all_data = {**metricas_dict, **estatisticas_dict, **intervalos_dict}
    df = pd.DataFrame(all_data)
    filename = "resultados.csv"
    filepath = os.path.join(assets_dir, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return filename

def main(num_servidores=2, nivel_confianca=0.95):
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
    ARQUIVO_DADOS = os.path.join(assets_dir, 'dados_atendimento.csv')
    
    # Executa simulação e análise do sistema de filas
    simulador = SimuladorFilas(num_servidores, ARQUIVO_DADOS)
    simulador.simular()
    metricas = simulador.calcular_metricas()
    simulador.gerar_graficos()
    
    # Realiza análise estatística dos dados
    analisador = AnalisadorEstatistico(ARQUIVO_DADOS)
    estatisticas = analisador.calcular_estatisticas_descritivas()
    analisador.gerar_visualizacoes()
    intervalos_confianca = analisador.calcular_intervalos_confianca(nivel_confianca)
    
    # Gera arquivo CSV com resultados
    csv_filename = generate_results_csv(metricas, estatisticas, intervalos_confianca)
    
    return metricas, estatisticas, intervalos_confianca, csv_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simular', methods=['POST'])
def simular():
    num_servidores = request.json.get('numServidores', 2)
    nivel_confianca = request.json.get('nivelConfianca', 0.95)
    metricas, estatisticas, intervalos_confianca, csv_filename = main(num_servidores, nivel_confianca)
    return jsonify({
        'metricas': metricas,
        'estatisticas': estatisticas,
        'intervalos_confianca': intervalos_confianca,
        'csv_filename': csv_filename
    })

@app.route('/download/<filename>')
def download_file(filename):
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
    return send_file(os.path.join(assets_dir, filename),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
    return send_from_directory(assets_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)