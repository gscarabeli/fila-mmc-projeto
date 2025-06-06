document.addEventListener('DOMContentLoaded', function() {
    const btnSimular = document.getElementById('btnSimular');
    const btnDownload = document.getElementById('btnDownload');
    const loading = document.getElementById('loading');
    const graphicsGrid = document.getElementById('graphics-grid');
    
    let currentCsvFilename = null;
    
    btnSimular.addEventListener('click', async function() {
        try {
            // Esconder gráficos e mostrar loading
            graphicsGrid.style.display = 'none';
            loading.style.display = 'block';
            btnSimular.disabled = true;
            btnSimular.style.opacity = '0.7';
            btnDownload.style.display = 'none';
            
            const numServidores = document.getElementById('numServidores').value;
            const nivelConfianca = document.getElementById('nivelConfianca').value;
            const response = await fetch('/simular', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    numServidores: parseInt(numServidores),
                    nivelConfianca: parseFloat(nivelConfianca)
                })
            });
            const data = await response.json();
            
            // Atualizar métricas
            const metricasDiv = document.getElementById('metricas');
            metricasDiv.innerHTML = formatarMetricas(data.metricas);
            
            // Atualizar estatísticas
            const estatisticasDiv = document.getElementById('estatisticas');
            estatisticasDiv.innerHTML = formatarEstatisticas(data.estatisticas);
            
            // Atualizar intervalos de confiança
            const intervalosDiv = document.getElementById('intervalos');
            intervalosDiv.innerHTML = formatarIntervalos(data.intervalos_confianca);
            
            // Salvar nome do arquivo CSV e mostrar botão de download
            currentCsvFilename = data.csv_filename;
            btnDownload.style.display = 'inline-block';
            
            // Atualizar imagens com um pequeno delay para garantir geração
            setTimeout(() => {
                const timestamp = new Date().getTime();
                document.getElementById('tempo-espera').src = '/assets/graphs/tempo_espera.png?' + timestamp;
                document.getElementById('tamanho-fila').src = '/assets/graphs/tamanho_fila.png?' + timestamp;
                document.getElementById('ocupacao-servidores').src = '/assets/graphs/ocupacao_servidores.png?' + timestamp;
                document.getElementById('histogramas-estatisticos').src = '/assets/graphs/histogramas_estatisticos.png?' + timestamp;
                document.getElementById('boxplot-estatistico').src = '/assets/graphs/boxplot_estatistico.png?' + timestamp;
                
                // Mostrar gráficos após carregar as imagens
                graphicsGrid.style.display = 'grid';
            }, 500);
            
        } catch (error) {
            alert('Erro ao executar simulação. Por favor, tente novamente.');
        } finally {
            // Esconder loading e reabilitar botão
            loading.style.display = 'none';
            btnSimular.disabled = false;
            btnSimular.style.opacity = '1';
        }
    });
    
    btnDownload.addEventListener('click', function() {
        if (currentCsvFilename) {
            window.location.href = `/download/${currentCsvFilename}`;
        }
    });
});

function formatarMetricas(metricas) {
    const ordem = ['P0', 'P_espera', 'Lq', 'Wq', 'W', 'L'];
    return ordem
        .map(chave => `<p><strong>${chave}:</strong> ${metricas[chave].toFixed(2).replace('.', ',')}</p>`)
        .join('');
}

function formatarEstatisticas(estatisticas) {
    const ordem = ['Média', 'Mediana', 'Moda', 'Variância', 'Desvio Padrão'];
    let html = '';
    
    // Ordem específica dos títulos
    const titulosOrdenados = [
        'Tempo de Chegada:',
        'Tempo de Atendimento:'
    ];
    
    for (const titulo of titulosOrdenados) {
        if (titulo in estatisticas) {
            html += `<h3 style="color: #2ecc71">${titulo}</h3>`;
            html += '<div class="stats-values">';
            html += ordem
                .map(metrica => {
                    const valor = estatisticas[titulo][metrica];
                    const formattedValue = typeof valor === 'number' ? valor.toFixed(2).replace('.', ',') : valor;
                    return `<p class="stat-item"><strong>${metrica}:</strong> <span class="value">${formattedValue}</span></p>`;
                })
                .join('');
            html += '</div>';
        }
    }
    
    return html;
}

function formatarIntervalos(intervalos) {
    // Ordem específica dos intervalos
    const titulosOrdenados = [
        'Tempo de Chegada:',
        'Tempo de Atendimento:'
    ];
    
    return titulosOrdenados
        .map(tipo => intervalos[tipo] ? `
            <h3 style="color: #2ecc71">${tipo}</h3>
            <p><strong>Limite inferior:</strong> ${intervalos[tipo].inferior.toFixed(2).replace('.', ',')}</p>
            <p><strong>Limite superior:</strong> ${intervalos[tipo].superior.toFixed(2).replace('.', ',')}</p>
        ` : '').join('');
}