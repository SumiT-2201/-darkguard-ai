console.log("DarkGuard ML Content Script Injected.");

// Listen for highlighting instructions from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "HIGHLIGHT_PATTERNS") {
        console.log("DarkGuard ML: Removing old highlights...");
        removeOldHighlights();
        
        const findings = request.findings || [];
        console.log(`DarkGuard ML: Highlighting ${findings.length} findings...`);
        
        findings.forEach(finding => {
            highlightOnPage(finding);
        });
    }
});

function removeOldHighlights() {
    document.querySelectorAll('.darkguard-highlight-wrap').forEach(el => {
        el.outerHTML = el.innerHTML; // Remove the wrapper, keep content
    });
    document.querySelectorAll('.darkguard-badge').forEach(el => el.remove());
}

function highlightOnPage(finding) {
    const textToFind = finding.matched_text.trim();
    if (!textToFind || textToFind.length < 5) return;

    // Search the whole DOM for elements containing the text
    // Note: This is an aggressive heuristic search
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
    
    let node;
    const nodesToHighlight = [];
    while (node = walker.nextNode()) {
        if (node.textContent.includes(textToFind)) {
            nodesToHighlight.push(node);
        }
    }

    nodesToHighlight.forEach(textNode => {
        const parent = textNode.parentElement;
        if (!parent || parent.classList.contains('darkguard-badge')) return;

        // Apply visual styling to parent
        parent.style.position = 'relative';
        parent.style.border = '2px solid #d63031'; // Red/Orange security theme
        parent.style.borderRadius = '4px';
        parent.style.padding = '2px';
        
        // Add Badge
        addBadge(parent, finding);
    });
}

function addBadge(element, finding) {
    const badge = document.createElement('div');
    badge.className = 'darkguard-badge';
    
    // Style the badge (Non-intrusive red/orange)
    Object.assign(badge.style, {
        position: 'absolute',
        top: '-12px',
        right: '-10px',
        backgroundColor: '#d63031',
        color: '#ffffff',
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '10px',
        fontWeight: 'bold',
        zIndex: '10000',
        cursor: 'help',
        boxShadow: '0 2px 4px rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        pointerEvents: 'auto'
    });

    const confidence = Math.round((finding.confidence || 0.8) * 100);
    const category = (finding.category || 'Deceptive').toUpperCase();
    
    badge.innerHTML = `
        <span>${category} (${confidence}%)</span> 
        <span style="font-style: normal; font-size: 11px;">ⓘ</span>
        <div class="dg-tooltip" style="
            display: none; 
            position: absolute; 
            top: 20px; 
            right: 0; 
            width: 200px; 
            background: #12121c; 
            color: #e2e2ec; 
            padding: 8px; 
            border: 1px solid #d63031; 
            border-radius: 4px; 
            z-index: 10001;
            font-weight: normal;
        ">
            <strong>Why was this flagged?</strong><br>
            ${finding.explanation || 'Semantic analysis identifies this as manipulative UI.'}
        </div>
    `;

    // Tooltip hover effect
    badge.addEventListener('mouseenter', () => {
        badge.querySelector('.dg-tooltip').style.display = 'block';
    });
    badge.addEventListener('mouseleave', () => {
        badge.querySelector('.dg-tooltip').style.display = 'none';
    });

    element.appendChild(badge);
}
