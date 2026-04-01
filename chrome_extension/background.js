chrome.runtime.onInstalled.addListener(() => {
    console.log("DarkGuard ML Chrome Extension Installed");
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "SCAN_CURRENT_PAGE") {
        // Fetch from our local backend API with security headers
        fetch("http://127.0.0.1:5000/api/scan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": request.apiKey || ""  // Send the user's API Key
            },
            body: JSON.stringify({ 
                url: request.url,
                threshold: request.threshold || 0.8 
            })
        })
        .then(response => response.json())
        .then(data => {
            // Forward back to popup AND to content script for UI highlights
            if (data.status === 'success' && data.report) {
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
            sendResponse({ status: "error", message: "Network error or unauthorized access." });
        });
        
        return true; // Keep message port open for async
    }
});
