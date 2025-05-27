from simulacao_filas import SimuladorFilas
from analise_estatistica import AnalisadorEstatistico
from flask import Flask, render_template, jsonify, send_from_directory, request, send_file
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

def generate_results_csv(metricas, estatisticas, intervalos_confianca):
    # Rename metrics with better labels
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
    
    # Flatten the nested dictionaries for statistics with better labels
    estatisticas_dict = {}
    medidas_labels = {
        'Média': 'Média',
        'Mediana': 'Mediana',
        'Moda': 'Moda',
        'Variância': 'Variância',
        'Desvio Padrão': 'Desvio Padrão'
    }
    for tipo, valores in estatisticas.items():
        tipo_clean = tipo.replace(':', '')  # Remove colon
        for metrica, valor in valores.items():
            col_name = f"{tipo_clean} - {medidas_labels.get(metrica, metrica)}"
            estatisticas_dict[col_name] = [valor]
    
    # Flatten the confidence intervals with better labels
    intervalos_dict = {}
    for tipo, valores in intervalos_confianca.items():
        tipo_clean = tipo.replace(':', '')  # Remove colon
        for limite, valor in valores.items():
            label = 'Limite Inferior' if limite == 'inferior' else 'Limite Superior'
            col_name = f"{tipo_clean} - {label}"
            intervalos_dict[col_name] = [valor]
    
    # Combine all dictionaries
    all_data = {**metricas_dict, **estatisticas_dict, **intervalos_dict}
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(all_data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"resultados_{timestamp}.csv"
    filepath = os.path.join("assets", filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')  # Using UTF-8 with BOM for Excel compatibility
    return filename

def main(num_servidores=3, nivel_confianca=0.95):
    # Configurações da simulação
    ARQUIVO_DADOS = 'assets/dados_atendimento.csv'
    
    # Executar simulação
    simulador = SimuladorFilas(num_servidores, ARQUIVO_DADOS)
    simulador.simular()
    metricas = simulador.calcular_metricas()
    simulador.gerar_graficos()
    
    # Executar análise estatística
    analisador = AnalisadorEstatistico(ARQUIVO_DADOS)
    estatisticas = analisador.calcular_estatisticas_descritivas()
    analisador.gerar_visualizacoes()
    intervalos_confianca = analisador.calcular_intervalos_confianca(nivel_confianca)
    
    # Generate CSV with results
    csv_filename = generate_results_csv(metricas, estatisticas, intervalos_confianca)
    
    return metricas, estatisticas, intervalos_confianca, csv_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simular', methods=['POST'])
def simular():
    num_servidores = request.json.get('numServidores', 3)
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
    return send_file(os.path.join('assets', filename),
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

if __name__ == '__main__':
    app.run(debug=True)