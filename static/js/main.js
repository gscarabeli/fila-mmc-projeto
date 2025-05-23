document.addEventListener('DOMContentLoaded', function() {
    const btnSimular = document.getElementById('btnSimular');
    const loading = document.getElementById('loading');
    const graphicsGrid = document.getElementById('graphics-grid');
    
    btnSimular.addEventListener('click', async function() {
        try {
            // Esconder gráficos e mostrar loading
            graphicsGrid.style.display = 'none';
            loading.style.display = 'block';
            btnSimular.disabled = true;
            btnSimular.style.opacity = '0.7';
            
            const response = await fetch('/simular');
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
            
            // Atualizar imagens
            const timestamp = new Date().getTime();
            document.getElementById('graficos-simulacao').src = '/assets/graficos_simulacao.png?' + timestamp;
            document.getElementById('graficos-estatisticos').src = '/assets/graficos_estatisticos.png?' + timestamp;
            
            // Mostrar gráficos após carregar as imagens
            graphicsGrid.style.display = 'grid';
            
        } catch (error) {
            console.error('Erro ao executar simulação:', error);
            alert('Erro ao executar simulação. Verifique o console para mais detalhes.');
        } finally {
            // Esconder loading e reabilitar botão
            loading.style.display = 'none';
            btnSimular.disabled = false;
            btnSimular.style.opacity = '1';
        }
    });
});

function formatarMetricas(metricas) {
    return Object.entries(metricas)
        .map(([chave, valor]) => `<p><strong>${chave}:</strong> ${valor.toFixed(2)}</p>`)
        .join('');
}

function formatarEstatisticas(estatisticas) {
    return Object.entries(estatisticas)
        .map(([tipo, dados]) => `
            <h4>${tipo}</h4>
            ${Object.entries(dados)
                .map(([chave, valor]) => `<p><strong>${chave}:</strong> ${valor.toFixed(2)}</p>`)
                .join('')}
        `).join('');
}

function formatarIntervalos(intervalos) {
    return Object.entries(intervalos)
        .map(([tipo, dados]) => `
            <h4>${tipo}</h4>
            <p><strong>Limite inferior:</strong> ${dados.inferior.toFixed(2)}</p>
            <p><strong>Limite superior:</strong> ${dados.superior.toFixed(2)}</p>
        `).join('');
}