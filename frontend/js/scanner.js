function startScan() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();
    
    if (!url) {
        showToast('Please enter a valid URL', 'error');
        return;
    }

    // Update UI
    const scanBtn = document.getElementById('scan-btn');
    const progress = document.getElementById('scan-progress');
    
    scanBtn.disabled = true;
    scanBtn.innerHTML = 'Scanning...';
    progress.classList.remove('hidden');

    // Make API request
    fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success' || data.status === 'partial') {
            showToast(data.status === 'success' ? 'Scan complete!' : 'Scan completed (with warnings)');
            renderReport(data.report);
            showView('report');
        } else {
            showToast('Scan Failed: ' + (data.message || 'System error occurred'), 'error');
        }
    })
    .catch(err => {
        console.error('Fetch Error:', err);
        showToast('Network Error: Could not reach the backend at http://127.0.0.1:5000. Please ensure the server is active.', 'error');
    })
    .finally(() => {
        scanBtn.disabled = false;
        scanBtn.innerHTML = '<span class="btn-text">Scan Now</span>';
        progress.classList.add('hidden');
    });
}

// Allow enter key
document.getElementById('url-input')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        startScan();
    }
});
