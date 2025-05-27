from simulacao_filas import SimuladorFilas
from analise_estatistica import AnalisadorEstatistico
from flask import Flask, render_template, jsonify, send_from_directory

app = Flask(__name__)

def main():
    # Configurações da simulação
    NUM_SERVIDORES = 3 #TODO: colocar como input do usuário
    ARQUIVO_DADOS = 'assets/dados_atendimento.csv'
    
    # Executar simulação
    simulador = SimuladorFilas(NUM_SERVIDORES, ARQUIVO_DADOS)
    simulador.simular()
    metricas = simulador.calcular_metricas()
    simulador.gerar_graficos()
    
    # Executar análise estatística
    analisador = AnalisadorEstatistico(ARQUIVO_DADOS)
    estatisticas = analisador.calcular_estatisticas_descritivas()
    analisador.gerar_visualizacoes()
    intervalos_confianca = analisador.calcular_intervalos_confianca()
    
    return metricas, estatisticas, intervalos_confianca

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simular')
def simular():
    metricas, estatisticas, intervalos_confianca = main()
    return jsonify({
        'metricas': metricas,
        'estatisticas': estatisticas,
        'intervalos_confianca': intervalos_confianca
    })

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

if __name__ == '__main__':
    app.run(debug=True)