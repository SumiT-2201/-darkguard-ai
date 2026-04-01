const API_BASE = 'http://127.0.0.1:5000/api';

function showView(viewId) {
    // Hide all views
    document.querySelectorAll('.view').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    
    // Show requested view
    const viewEl = document.getElementById(`view-${viewId}`);
    if (viewEl) {
        viewEl.classList.remove('hidden');
        // trigger reflow
        void viewEl.offsetWidth;
        viewEl.classList.add('active');
    }
    
    const navEl = document.getElementById(`nav-${viewId}`);
    if (navEl) {
        navEl.classList.add('active');
    }

    if (viewId === 'history') {
        loadHistory();
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.remove('hidden');
    
    if (type === 'error') {
        toast.style.borderColor = 'var(--danger)';
    } else {
        toast.style.borderColor = 'var(--accent)';
    }

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function getGradeColor(grade) {
    const colors = {
        'A': 'var(--success)',
        'B': '#55efc4',
        'C': 'var(--warning)',
        'D': '#ff7675',
        'F': 'var(--danger)'
    };
    return colors[grade] || 'var(--text-secondary)';
}

async function loadHistory() {
    const listEl = document.getElementById('history-list');
    listEl.innerHTML = '<div class="progress-spinner" style="margin:2rem auto"></div>';

    try {
        const res = await fetch(`${API_BASE}/history`, { method: 'GET' });
        const data = await res.json();
        
        console.log('History data received:', data);

        if (data.success) {
            const historyData = data.data || [];
            
            if (historyData.length === 0) {
                listEl.innerHTML = '<div class="empty-state">No scans in history yet.</div>';
            } else {
                listEl.innerHTML = historyData.map(item => `
                    <div class="history-item" onclick="loadReport('${item.id || item._id}')">
                        <div class="history-info">
                            <h3>${item.domain || item.url}</h3>
                            <div class="history-meta">
                                📅 ${new Date(item.timestamp || item.scan_date).toLocaleString()} 
                                &bull; <span style="color:var(--text-secondary)">${item.url}</span>
                            </div>
                        </div>
                        <div class="history-score">
                            <div class="history-grade" style="background:${getGradeColor(item.grade)}20;color:${getGradeColor(item.grade)}">Grade ${item.grade}</div>
                            <div style="font-weight:800; font-size:1.1rem">${item.trust_score || 0}/100</div>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            console.error('History API error:', data.message);
            listEl.innerHTML = `<div class="error">Failed to load: ${data.message || 'Unknown error'}</div>`;
        }
    } catch (err) {
        console.error('Fetch error:', err);
        listEl.innerHTML = '<div class="error">Could not connect to backend at http://127.0.0.1:5000</div>';
    }
}

async function loadReport(id) {
    showToast('Loading report...');
    try {
        const res = await fetch(`${API_BASE}/report/${id}`);
        const data = await res.json();
        
        if (data.status === 'success') {
            renderReport(data.report);
            showView('report');
        } else {
            showToast(data.message || 'Report not found', 'error');
        }
    } catch (err) {
        console.error('Report fetch error:', err);
        showToast('Network error while loading report', 'error');
    }
}
