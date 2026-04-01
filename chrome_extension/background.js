chrome.runtime.onInstalled.addListener(() => {
    console.log("DarkGuard ML Chrome Extension Installed");
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "SCAN_CURRENT_PAGE") {
        // Fetch from our local backend API
        fetch("http://127.0.0.1:5000/api/scan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                url: request.url,
                threshold: request.threshold || 0.8 
            })
        })
        .then(response => response.json())
        .then(data => {
            // Forward the result back to the popup AND to the content script for highlighting
            if (data.status === 'success') {
                chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                    if (tabs[0]) {
                        chrome.tabs.sendMessage(tabs[0].id, {
                            type: "HIGHLIGHT_PATTERNS",
                            findings: data.report.findings_list
                        });
                    }
                });
            }
            sendResponse(data);
        })
        .catch(error => {
            console.error("Fetch Error:", error);
            sendResponse({ status: "error", message: error.toString() });
        });
        
        return true; // Keep message port open for async
    }
});
