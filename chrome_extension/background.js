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
            body: JSON.stringify({ url: request.url })
        })
        .then(response => response.json())
        .then(data => sendResponse(data))
        .catch(error => sendResponse({ status: "error", message: error.toString() }));
        
        return true; // Keep message port open for async
    }
});
