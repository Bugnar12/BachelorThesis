/* badge helper */
function setBadge(state) {
    const cfg = {
        phishing: { text: "⚠", color: "#f39c12" },
        safe:     { text: "✔", color: "#43a047" },
        none:     { text: "",  color: "#666" }
    };
    chrome.action.setBadgeText({ text: cfg[state].text });
    chrome.action.setBadgeBackgroundColor({ color: cfg[state].color });
}

/* receive verdicts from the content-script */
chrome.runtime.onMessage.addListener((msg, sender) => {
    if (msg.type === "PHISHING_VERDICT") {
        setBadge(msg.verdict);                 // "phishing" | "safe"
    }
});

/* context-menu for manual scan */
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scan-again",
        title: "Scan this email again",
        contexts: ["action"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-again") {
        chrome.tabs.sendMessage(tab.id, { type: "TRIGGER_SCAN" });
    }
});
