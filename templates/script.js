// Estado de la aplicación
const state = {
    analysisActive: false,
    isLoading: false,
    currentAnalysis: null,
    currentJobId: null,
    targetIp: '',
    scanType: 'basic',
    investigationStartTime: null,
    investigationInterval: null
};

// Elementos del DOM
let initialView, analysisView, searchInput, searchBtn, closeBtn, loadingIndicator, loadingText;
let suggestions, tabBtns, scanRadios, downloadTxtBtn, downloadPdfBtn;
let investigationPanel, investigationLogs, investigationTimer;

function initializeDOM() {
    initialView = document.getElementById('initialView');
    analysisView = document.getElementById('analysisView');
    searchInput = document.getElementById('searchInput');
    searchBtn = document.getElementById('searchBtn');
    closeBtn = document.getElementById('closeBtn');
    loadingIndicator = document.getElementById('loadingIndicator');
    loadingText = document.getElementById('loadingText');
    suggestions = document.querySelectorAll('.suggestion-item');
    tabBtns = document.querySelectorAll('.tab-btn');
    scanRadios = document.querySelectorAll('input[name="scanType"]');
    downloadTxtBtn = document.getElementById('downloadTxt');
    downloadPdfBtn = document.getElementById('downloadPdf');
    investigationPanel = document.getElementById('investigationPanel');
    investigationLogs = document.getElementById('investigationLogs');
    investigationTimer = document.getElementById('investigationTimer');
    
    console.log('✓ DOM elementos inicializados correctamente');
}

// Funciones para el panel de investigación
function showInvestigationPanel() {
    investigationPanel.classList.add('active');
    state.investigationStartTime = Date.now();
    
    // Actualizar timer cada segundo
    state.investigationInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - state.investigationStartTime) / 1000);
        const mins = Math.floor(elapsed / 60);
        const secs = elapsed % 60;
        investigationTimer.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    }, 100);
    
    // Limpiar logs anteriores
    investigationLogs.innerHTML = '';
}

function hideInvestigationPanel() {
    investigationPanel.classList.remove('active');
    if (state.investigationInterval) {
        clearInterval(state.investigationInterval);
        state.investigationInterval = null;
    }
}

function addInvestigationLog(message, type = 'searching') {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    
    const icon = document.createElement('div');
    icon.className = 'log-icon';
    
    const text = document.createElement('div');
    text.className = 'log-text';
    text.innerHTML = message;
    
    // Agregar icono según el tipo
    if (type === 'searching') {
        icon.innerHTML = '⏳';
    } else if (type === 'success') {
        icon.innerHTML = '✓';
    } else if (type === 'error') {
        icon.innerHTML = '✗';
    }
    
    logEntry.appendChild(icon);
    logEntry.appendChild(text);
    investigationLogs.appendChild(logEntry);
    
    // Auto-scroll al final
    investigationLogs.scrollTop = investigationLogs.scrollHeight;
}

// Event Listeners para la vista inicial
function attachEventListeners() {
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && searchInput.value.trim()) {
            startAnalysis(searchInput.value.trim());
        }
    });

    searchBtn.addEventListener('click', () => {
        console.log('Button clicked! Value:', searchInput.value.trim());
        if (searchInput.value.trim()) {
            startAnalysis(searchInput.value.trim());
        }
    });

    // Event Listeners para las sugerencias
    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', () => {
            startAnalysis(suggestion.textContent);
        });
    });

    // Event Listeners para los tabs
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    // Event Listeners para tipo de escaneo
    scanRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            state.scanType = e.target.value;
        });
    });

    // Event Listeners para botones de descarga
    downloadTxtBtn.addEventListener('click', () => downloadReport('txt'));
    downloadPdfBtn.addEventListener('click', () => downloadReport('pdf'));

    // Event Listener para cerrar
    closeBtn.addEventListener('click', closeAnalysis);
    
    console.log('✓ Event listeners inicializados correctamente');
}

// Funciones principales
function startAnalysis(targetIp) {
    state.targetIp = targetIp;
    state.analysisActive = true;
    
    // Mostrar análisis, ocultar inicial
    initialView.classList.add('hidden');
    analysisView.classList.add('active');
    
    // Mostrar loading y panel de investigación
    loadingIndicator.classList.add('show');
    showInvestigationPanel();
    
    // Actualizar header
    document.getElementById('targetIp').textContent = targetIp;
    document.getElementById('scanBadge').textContent = state.scanType === 'basic' 
        ? 'Escaneo Básico' 
        : 'Escaneo Profundo';
    
    // Hacer petición a FastAPI
    fetchAnalysis(targetIp);
}

function fetchAnalysis(targetIp) {
    const payload = {
        target_ip: targetIp,
        scan_type: state.scanType
    };
    
    const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? `http://localhost:8001/api/analyze`
        : `${window.location.origin}/api/analyze`;
    
    // Agregar logs iniciales
    addInvestigationLog(`<strong>Iniciando análisis de ${targetIp}</strong>`, 'searching');
    const scanTypeText = state.scanType === 'basic' ? 'Escaneo Básico' : 'Escaneo Profundo';
    addInvestigationLog(`Tipo de escaneo: <strong>${scanTypeText}</strong>`, 'searching');
    addInvestigationLog(`Conectando a API...`, 'searching');
    
    // Crear AbortController con timeout de 30 minutos (1800000ms)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1800000);
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: controller.signal
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        clearTimeout(timeoutId);
        
        // La API ahora retorna un job_id encriptado en nmap_output
        // Extraemos el job_id si está disponible
        const jobIdMatch = data.nmap_output?.match(/Job ([a-f0-9-]+) encolado/);
        if (jobIdMatch && jobIdMatch[1]) {
            state.currentJobId = jobIdMatch[1];
            addInvestigationLog(`✓ Job encolado: ${state.currentJobId.substring(0, 8)}...`, 'success');
            
            // Iniciar polling de logs por job
            pollJobLogs(state.currentJobId);
        } else {
            // Fallback: si no hay job_id, mostrar datos directamente (compatible con versión anterior)
            state.currentAnalysis = data;
            loadingIndicator.classList.remove('show');
            addInvestigationLog(`✓ Análisis completado exitosamente`, 'success');
            
            setTimeout(() => {
                hideInvestigationPanel();
                displayResults(data);
                switchTab('analysis');
            }, 800);
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        loadingIndicator.classList.remove('show');
        console.error('Error:', error);
        
        addInvestigationLog(`Error: ${error.message}`, 'error');
        
        let errorMsg = error.message;
        let suggestion = '';
        
        if (error.message.includes('504') || error.message.includes('timeout')) {
            suggestion = '<br><strong>Tip:</strong> El análisis tardó demasiado. Intenta:<br>• Usar Escaneo Básico en lugar de Profundo<br>• Esperar a que Ollama termine (checa la terminal)';
        } else if (error.message.includes('500')) {
            suggestion = '<br><strong>Tip:</strong> Error en el servidor. Verifica:<br>• Logs de FastAPI en la terminal<br>• Que Nmap y Ollama estén instalados';
        }
        
        document.getElementById('analysis-tab').innerHTML = `
            <div style="color: #ff6b6b; padding: 20px; border-radius: 8px; background: rgba(255,107,107,0.1); border: 1px solid rgba(255,107,107,0.3);">
                <strong>❌ Error en la conexión:</strong><br>
                ${errorMsg}
                ${suggestion}<br><br>
                <strong>Requisitos:</strong><br>
                • FastAPI corriendo en http://localhost:8001<br>
                • Ollama activo (ollama serve)<br>
                • Nmap instalado (sudo apt install nmap)<br>
                • Puertos 8001 disponibles
            </div>
        `;
        switchTab('analysis');
    });
}

function pollJobLogs(jobId) {
    // Hace polling de los logs del job cada 500ms hasta que esté completado
    let lastLogCount = 0;
    let pollAttempts = 0;
    const maxPollAttempts = 3600; // 30 min * 60 * 2 (polling cada 500ms)
    
    const logsBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? `http://localhost:8001/api/jobs/${jobId}`
        : `${window.location.origin}/api/jobs/${jobId}`;
    
    const logPoller = setInterval(() => {
        pollAttempts++;
        if (pollAttempts > maxPollAttempts) {
            clearInterval(logPoller);
            addInvestigationLog('Error: Timeout en el análisis (superó 30 minutos)', 'error');
            return;
        }
        
        // Obtener logs
        fetch(`${logsBaseUrl}/logs`)
            .then(r => r.json())
            .then(data => {
                const logs = data.logs || [];
                if (logs.length > lastLogCount) {
                    for (let i = lastLogCount; i < logs.length; i++) {
                        const log = logs[i];
                        const logType = log.type === 'error' ? 'error' : log.type === 'searching' ? 'searching' : 'success';
                        addInvestigationLog(log.message, logType);
                    }
                    lastLogCount = logs.length;
                }
            })
            .catch(() => {}); // Ignorar errores de polling
        
        // Verificar estado del job
        fetch(`${logsBaseUrl}/status`)
            .then(r => r.json())
            .then(data => {
                if (data.status === 'completed') {
                    clearInterval(logPoller);
                    loadingIndicator.classList.remove('show');
                    addInvestigationLog(`✓ Análisis completado exitosamente`, 'success');
                    
                    // Obtener resultado completo
                    fetch(`${logsBaseUrl}/result`)
                        .then(r => r.json())
                        .then(result => {
                            state.currentAnalysis = result;
                            setTimeout(() => {
                                hideInvestigationPanel();
                                displayResults(result);
                                switchTab('analysis');
                            }, 800);
                        });
                } else if (data.status === 'error') {
                    clearInterval(logPoller);
                    loadingIndicator.classList.remove('show');
                    addInvestigationLog(`✗ Error: ${data.error}`, 'error');
                }
            })
            .catch(() => {}); // Ignorar errores
    }, 500); // Polling cada 500ms
}

function displayResults(data) {
    // Tab Análisis
    document.getElementById('analysisText').textContent = data.analysis;
    
    // Tab Nmap
    document.getElementById('nmapOutput').textContent = data.nmap_output;
    
    // Tab Exploits
    displayExploits(data.exploits);
}

function displayExploits(exploits) {
    const exploitsList = document.getElementById('exploitsList');
    exploitsList.innerHTML = '';
    
    if (!exploits || exploits.length === 0) {
        exploitsList.innerHTML = '<p style="color: rgba(255,255,255,0.6);">No se encontraron exploits</p>';
        return;
    }
    
    exploits.forEach(group => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'exploit-group';
        
        const serviceDiv = document.createElement('div');
        serviceDiv.className = 'exploit-service';
        serviceDiv.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12h6m0 0h6m-6-6v6m0 0v6"></path>
            </svg>
            ${group.service}
        `;
        
        groupDiv.appendChild(serviceDiv);
        
        group.exploits.forEach(exploit => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'exploit-item';
            if (typeof exploit === 'object') {
                itemDiv.textContent = `${exploit.description} (${exploit.file})`;
            } else {
                itemDiv.textContent = exploit;
            }
            groupDiv.appendChild(itemDiv);
        });
        
        exploitsList.appendChild(groupDiv);
    });
}

function switchTab(tabName) {
    // Desactivar todos los tabs
    tabBtns.forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    
    // Activar el tab seleccionado
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

function downloadReport(format) {
    if (!state.currentAnalysis) return;
    
    downloadTxtBtn.disabled = true;
    downloadPdfBtn.disabled = true;
    
    const exploitsJson = JSON.stringify(state.currentAnalysis.exploits);
    
    const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? `http://localhost:8001/api/save-report`
        : `${window.location.origin}/api/save-report`;
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            target_ip: state.targetIp,
            nmap_output: state.currentAnalysis.nmap_output,
            analysis: state.currentAnalysis.analysis,
            exploits: exploitsJson,
            format: format
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Reporte guardado: ${data.filename}`);
        }
        downloadTxtBtn.disabled = false;
        downloadPdfBtn.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al descargar el reporte');
        downloadTxtBtn.disabled = false;
        downloadPdfBtn.disabled = false;
    });
}

function closeAnalysis() {
    state.analysisActive = false;
    
    // Ocultar análisis, mostrar inicial
    initialView.classList.remove('hidden');
    analysisView.classList.remove('active');
    
    // Limpiar
    searchInput.value = '';
    state.currentAnalysis = null;
    
    // Enfocar búsqueda
    setTimeout(() => searchInput.focus(), 300);
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    initializeDOM();
    attachEventListeners();
    searchInput.focus();
    console.log('✓ Aplicación lista');
});

// Fallback por si el DOMContentLoaded no se dispara
window.addEventListener('load', () => {
    // Verificar si ya se inicializó
    if (!searchInput || !searchBtn.onclick) {
        initializeDOM();
        attachEventListeners();
    }
    searchInput.focus();
});
