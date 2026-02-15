// WebSocket connection
let ws = null;
let reconnectInterval = null;
const WS_URL = `ws://${window.location.host}/ws`;

// System state
const systemState = {
    databaseMode: 'unknown', // 'postgres', 'memory', or 'unknown'
    apiHealthy: true,
    lastHealthCheck: null
};

// State
const state = {
    stats: {
        success: 0,
        processing: 0,
        skipped: 0,
        failed: 0
    },
    incidents: new Map(),
    history: []
};

// DOM Elements
const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    connectionText: document.getElementById('connectionText'),
    statSuccess: document.getElementById('statSuccess'),
    statProcessing: document.getElementById('statProcessing'),
    statSkipped: document.getElementById('statSkipped'),
    statFailed: document.getElementById('statFailed'),
    liveFeed: document.getElementById('liveFeed'),
    logsConsole: document.getElementById('logsConsole'),
    historyBody: document.getElementById('historyBody'),
    clearFeed: document.getElementById('clearFeed'),
    clearLogs: document.getElementById('clearLogs'),
    refreshHistory: document.getElementById('refreshHistory'),
    searchHistory: document.getElementById('searchHistory'),
    systemBanner: document.getElementById('systemBanner'),
    bannerMessage: document.getElementById('bannerMessage'),
    closeBanner: document.getElementById('closeBanner'),
    notificationContainer: document.getElementById('notificationContainer')
};

// Initialize
function init() {
    checkSystemHealth();
    connectWebSocket();
    loadHistory();
    loadStatistics();
    setupEventListeners();

    // Auto-refresh history every 30 seconds
    setInterval(loadHistory, 30000);

    // Health check every 60 seconds
    setInterval(checkSystemHealth, 60000);
}

// WebSocket Connection
function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            console.log('WebSocket connected');
            updateConnectionStatus(true);
            clearReconnectInterval();
            addLog('info', 'Connected to incident handler stream');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            addLog('error', 'WebSocket connection error');
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            updateConnectionStatus(false);
            addLog('warning', 'Disconnected from stream. Attempting to reconnect...');
            scheduleReconnect();
        };
    } catch (error) {
        console.error('Failed to connect:', error);
        updateConnectionStatus(false);
        scheduleReconnect();
    }
}

function scheduleReconnect() {
    if (!reconnectInterval) {
        reconnectInterval = setInterval(() => {
            console.log('Attempting to reconnect...');
            connectWebSocket();
        }, 5000);
    }
}

function clearReconnectInterval() {
    if (reconnectInterval) {
        clearInterval(reconnectInterval);
        reconnectInterval = null;
    }
}

function updateConnectionStatus(connected) {
    if (connected) {
        elements.connectionStatus.classList.add('connected');
        elements.connectionStatus.classList.remove('disconnected');
        elements.connectionText.textContent = 'Connected';
    } else {
        elements.connectionStatus.classList.remove('connected');
        elements.connectionStatus.classList.add('disconnected');
        elements.connectionText.textContent = 'Disconnected';
    }
}

// System Health Check
async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');

        if (!response.ok) {
            throw new Error(`Health check failed: ${response.status}`);
        }

        const health = await response.json();
        systemState.apiHealthy = true;
        systemState.lastHealthCheck = new Date();

        // Check database mode
        if (health.database_mode) {
            const previousMode = systemState.databaseMode;
            systemState.databaseMode = health.database_mode;

            // Show banner if using in-memory mode
            if (health.database_mode === 'memory' && previousMode !== 'memory') {
                showSystemBanner(
                    'warning',
                    '⚠️ Running in In-Memory Mode: Database connection unavailable. Data will not persist after restart.',
                    true
                );
                addLog('warning', 'System is using in-memory storage. Data will not persist.');
            } else if (health.database_mode === 'postgres' && previousMode === 'memory') {
                showSystemBanner(
                    'success',
                    '✓ Database Connected: System is now using PostgreSQL. Data will persist.',
                    false
                );
                addLog('success', 'Database connection restored.');
            }
        }

    } catch (error) {
        console.error('Health check failed:', error);
        systemState.apiHealthy = false;

        // Show error notification
        showNotification(
            'error',
            'API Connection Error',
            'Unable to reach the backend API. Please check if the server is running.',
            15000
        );

        addLog('error', `Health check failed: ${error.message}`);
    }
}

function showSystemBanner(type, message, persistent = false) {
    elements.bannerMessage.textContent = message;
    elements.systemBanner.className = `system-banner ${type}`;
    elements.systemBanner.style.display = 'block';

    // Auto-hide success messages after 10 seconds
    if (!persistent && type === 'success') {
        setTimeout(() => {
            elements.systemBanner.style.display = 'none';
        }, 10000);
    }
}

function hideSystemBanner() {
    elements.systemBanner.style.display = 'none';
}

// Notification System
function showNotification(type, title, message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    notification.innerHTML = `
        <div class="notification-icon">${icons[type] || icons.info}</div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close">✕</button>
    `;

    elements.notificationContainer.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);

    // Close button
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => removeNotification(notification));

    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => removeNotification(notification), duration);
    }
}

function removeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
}


// WebSocket Message Handler
function handleWebSocketMessage(message) {
    const { type, data, timestamp } = message;

    switch (type) {
        case 'execution_started':
            handleExecutionStarted(data);
            break;
        case 'incident_processing':
            handleIncidentProcessing(data);
            break;
        case 'rule_matched':
            handleRuleMatched(data);
            break;
        case 'incident_resolved':
            handleIncidentResolved(data);
            break;
        case 'incident_skipped':
            handleIncidentSkipped(data);
            break;
        case 'error_occurred':
            handleError(data);
            break;
        case 'execution_completed':
            handleExecutionCompleted(data);
            break;
    }
}

function handleExecutionStarted(data) {
    addLog('info', `Execution started: ${data.total_incidents} incidents to process`);
    state.stats.processing = data.total_incidents;
    updateStats();
}

function handleIncidentProcessing(data) {
    const { incident_number, short_description } = data;

    // Add to live feed
    addIncidentCard(incident_number, short_description, 'processing');

    addLog('info', `Processing ${incident_number}: ${short_description}`);
}

function handleRuleMatched(data) {
    const { incident_number, rule } = data;

    updateIncidentCard(incident_number, 'processing',
        `Matched rule - ${rule.closure_note || 'Resolving...'}`);

    addLog('success', `Rule matched for ${incident_number}`);
}

function handleIncidentResolved(data) {
    const { incident_number } = data;

    updateIncidentCard(incident_number, 'success', 'Successfully resolved');

    state.stats.success++;
    state.stats.processing = Math.max(0, state.stats.processing - 1);
    updateStats();

    addLog('success', `✓ Resolved ${incident_number}`);

    // Reload history to show new entry
    setTimeout(loadHistory, 1000);
}

function handleIncidentSkipped(data) {
    const { incident_number, reason } = data;

    updateIncidentCard(incident_number, 'skipped', reason);

    state.stats.skipped++;
    state.stats.processing = Math.max(0, state.stats.processing - 1);
    updateStats();

    addLog('warning', `⊘ Skipped ${incident_number}: ${reason}`);

    setTimeout(loadHistory, 1000);
}

function handleError(data) {
    const { incident_number, error } = data;

    updateIncidentCard(incident_number, 'error', error);

    state.stats.failed++;
    state.stats.processing = Math.max(0, state.stats.processing - 1);
    updateStats();

    addLog('error', `✕ Error on ${incident_number}: ${error}`);

    setTimeout(loadHistory, 1000);
}

function handleExecutionCompleted(data) {
    const { stats } = data;

    addLog('info', `Execution completed - Success: ${stats.success}, Failed: ${stats.failed}, Skipped: ${stats.skipped}`);

    state.stats.processing = 0;
    updateStats();
}

// UI Updates
function updateStats() {
    elements.statSuccess.textContent = state.stats.success;
    elements.statProcessing.textContent = state.stats.processing;
    elements.statSkipped.textContent = state.stats.skipped;
    elements.statFailed.textContent = state.stats.failed;
}

function addIncidentCard(number, description, status) {
    // Remove empty state if present
    const emptyState = elements.liveFeed.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const card = document.createElement('div');
    card.className = `incident-card ${status}`;
    card.id = `incident-${number}`;

    card.innerHTML = `
        <div class="incident-header">
            <span class="incident-number">${number}</span>
            <span class="incident-status ${status}">${status}</span>
        </div>
        <div class="incident-description">${description}</div>
        <div class="incident-time">${new Date().toLocaleTimeString()}</div>
    `;

    elements.liveFeed.insertBefore(card, elements.liveFeed.firstChild);

    // Keep only last 50 incidents
    const cards = elements.liveFeed.querySelectorAll('.incident-card');
    if (cards.length > 50) {
        cards[cards.length - 1].remove();
    }

    state.incidents.set(number, card);
}

function updateIncidentCard(number, status, additionalInfo) {
    const card = state.incidents.get(number);
    if (!card) return;

    card.className = `incident-card ${status}`;

    const statusElement = card.querySelector('.incident-status');
    if (statusElement) {
        statusElement.className = `incident-status ${status}`;
        statusElement.textContent = status;
    }

    if (additionalInfo) {
        const description = card.querySelector('.incident-description');
        if (description) {
            description.textContent = additionalInfo;
        }
    }
}

function addLog(level, message) {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${level}`;

    const time = new Date().toLocaleTimeString();
    logEntry.innerHTML = `
        <span class="log-time">[${time}]</span>
        <span class="log-message">${message}</span>
    `;

    elements.logsConsole.insertBefore(logEntry, elements.logsConsole.firstChild);

    // Keep only last 100 logs
    const logs = elements.logsConsole.querySelectorAll('.log-entry');
    if (logs.length > 100) {
        logs[logs.length - 1].remove();
    }
}

// API Calls with Error Handling
async function loadHistory() {
    try {
        const response = await fetch('/api/history?limit=100');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const history = await response.json();
        state.history = history;
        renderHistory(history);

    } catch (error) {
        console.error('Failed to load history:', error);
        addLog('error', 'Failed to load processing history');

        // Show user-friendly error
        showNotification(
            'error',
            'History Load Failed',
            'Unable to load incident processing history. The data may be temporarily unavailable.',
            8000
        );

        // Show fallback UI
        renderHistoryError(error.message);
    }
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const stats = await response.json();

        if (stats.today) {
            state.stats.success = stats.today.success || 0;
            state.stats.skipped = stats.today.skipped || 0;
            state.stats.failed = stats.today.failed || 0;
            updateStats();
        }

    } catch (error) {
        console.error('Failed to load statistics:', error);
        addLog('warning', 'Statistics temporarily unavailable');

        // Don't show notification for stats failure (less critical)
        // Stats will show 0 which is acceptable fallback
    }
}

function renderHistory(history) {
    if (history.length === 0) {
        elements.historyBody.innerHTML = '<tr class="empty-row"><td colspan="5">No processing history yet</td></tr>';
        return;
    }

    elements.historyBody.innerHTML = history.map(item => `
        <tr>
            <td><strong>${item.incident_number || 'N/A'}</strong></td>
            <td>${truncate(item.short_description || 'N/A', 60)}</td>
            <td><span class="status-badge ${item.status}">${item.status}</span></td>
            <td>${item.action_taken || 'N/A'}</td>
            <td>${formatDate(item.processed_at)}</td>
        </tr>
    `).join('');
}

function renderHistoryError(errorMessage) {
    elements.historyBody.innerHTML = `
        <tr class="error-row">
            <td colspan="5">
                <div class="error-state">
                    <div class="error-icon">⚠️</div>
                    <div class="error-title">Unable to Load History</div>
                    <div class="error-message">${errorMessage}</div>
                    <button class="btn-retry" onclick="loadHistory()">↻ Retry</button>
                </div>
            </td>
        </tr>
    `;
}

function truncate(str, length) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Event Listeners
function setupEventListeners() {
    elements.clearFeed.addEventListener('click', () => {
        elements.liveFeed.innerHTML = '<div class="empty-state"><div class="empty-icon">📊</div><p>Waiting for incidents to process...</p></div>';
        state.incidents.clear();
        addLog('info', 'Live feed cleared');
    });

    elements.clearLogs.addEventListener('click', () => {
        elements.logsConsole.innerHTML = '<div class="log-entry info"><span class="log-time">[' + new Date().toLocaleTimeString() + ']</span><span class="log-message">Logs cleared</span></div>';
        addLog('info', 'Logs cleared');
    });

    elements.refreshHistory.addEventListener('click', () => {
        loadHistory();
        loadStatistics();
        addLog('info', 'History refreshed');
    });

    elements.searchHistory.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = state.history.filter(item =>
            (item.incident_number && item.incident_number.toLowerCase().includes(query)) ||
            (item.short_description && item.short_description.toLowerCase().includes(query))
        );
        renderHistory(filtered);
    });

    elements.closeBanner.addEventListener('click', () => {
        hideSystemBanner();
    });
}

// Start the application
init();
