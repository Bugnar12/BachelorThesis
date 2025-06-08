console.log("[EXTENSION] Content script loaded.");

let lastAnalyzedEmail = '';
let autoScan = true;

chrome.storage.sync.get('autoScan', d => {
    if (typeof d.autoScan === 'boolean') autoScan = d.autoScan;
});

function insertVerdictLabel(verdict, textPrediction, urlPrediction, vtPrediction) {
    if (document.getElementById("phishing-verdict-label")) return;
    const subjectBar = document.querySelector('h2[data-legacy-thread-id]');
    if (!subjectBar) return;

    const verdictEl = document.createElement("div");
    verdictEl.id = "phishing-verdict-label";
    const icon = verdict === "phishing" ? "⚠️" : (verdict === "legitimate" ? "✅" : "❓");
    console.log(verdict)
    const labelText = verdict === "phishing"
        ? "Potential Phishing"
        : (verdict === "legitimate" ? "Likely Safe" : "Server Unavailable");
    verdictEl.textContent = `${icon} ${labelText}`;

    const tooltip = document.createElement("div");
    tooltip.innerText = `Text Verdict: ${textPrediction}\nURL Verdict: ${urlPrediction}\nVT Verdict: ${vtPrediction}`;
    Object.assign(tooltip.style, {
        position: "absolute",
        backgroundColor: "#333",
        color: "#fff",
        padding: "5px 10px",
        borderRadius: "6px",
        fontSize: "12px",
        whiteSpace: "pre-line",
        zIndex: "9999",
        display: "none",
        maxWidth: "320px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.3)"
    });

    verdictEl.addEventListener("mouseenter", e => {
        tooltip.style.left = `${e.pageX + 10}px`;
        tooltip.style.top = `${e.pageY + 10}px`;
        tooltip.style.display = "block";
        document.body.appendChild(tooltip);
    });
    verdictEl.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
        tooltip.remove();
    });

    let bgColor = "#e7fce7";      // default for legitimate
    let borderColor = "#5cb85c";  // green for legitimate

    if (verdict === "phishing") {
        bgColor = "#ffe5e5";
        borderColor = "#d9534f";
    } else if (verdict === "unknown") {
        bgColor = "#f2f2f2";       // light gray background
        borderColor = "#999";      // gray border
    }

    Object.assign(verdictEl.style, {
        padding: "12px",
        marginBottom: "12px",
        backgroundColor: bgColor,
        border: `2px solid ${borderColor}`,
        fontWeight: "600",
        fontSize: "15px",
        cursor: "help",
        whiteSpace: "pre-line",
        borderRadius: "8px",
        maxWidth: "420px",
        boxShadow: "0 3px 8px rgba(0,0,0,0.1)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "12px"
    });


    const reportBtn = document.createElement("button");
    reportBtn.innerText = "Report False Positive";
    Object.assign(reportBtn.style, {
        padding: "6px 12px",
        fontSize: "13px",
        cursor: "pointer",
        backgroundColor: "#f0f0f0",
        border: "1px solid #ccc",
        borderRadius: "6px",
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
    });

    reportBtn.onclick = () => {
        fetch("https://bachelorthesis-production-8acf.up.railway.app/emails/report-fp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ subject: subjectBar.innerText, verdict, timestamp: Date.now() })
        }).then(() => {
            reportBtn.innerText = "Reported!";
            reportBtn.disabled = true;
            reportBtn.style.backgroundColor = "#d0ffd0";
        }).catch(() => {
            reportBtn.innerText = "Error";
            reportBtn.style.backgroundColor = "#ffd0d0";
        });
    };

    verdictEl.appendChild(reportBtn);
    subjectBar.parentElement.insertBefore(verdictEl, subjectBar);
}

function performScan(forced = false) {
    if (!autoScan && !forced) return;

    // Selct the DOM elements that contain relevant email fields
    const subjectNode = document.querySelector('h2[data-legacy-thread-id]');
    const bodyContainer = document.querySelector('div.a3s');
    const senderNode = document.querySelector('.gD');
    if (!subjectNode || !bodyContainer) return;

    // Extract the actual content from DOM nodes
    const subject = subjectNode.innerText;
    const sender = senderNode ? senderNode.getAttribute('email') || senderNode.innerText : '';
    const uniqueKey = subject + '|' + sender;
    if (!forced && uniqueKey === lastAnalyzedEmail) return;
    lastAnalyzedEmail = uniqueKey;

    let body = bodyContainer.innerHTML;
    const possibleDeepDiv = bodyContainer.querySelector('div[dir="ltr"]');
    if (possibleDeepDiv) body = possibleDeepDiv.innerHTML;

    fetch("https://bachelorthesis-production-8acf.up.railway.app/emails/predict/email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, sender, body })
    })
        .then(res => res.json())
        .then(data => {
            insertVerdictLabel(data.verdict, data.text_prediction, data.url_prediction, data.vt_prediction);
            chrome.runtime.sendMessage({ type: "PHISHING_VERDICT", verdict: data.verdict === "phishing" ? "phishing" : "safe" });
        })
        .catch(err => {
            console.error("[EXTENSION] Prediction error:", err)
            insertVerdictLabel("unknown", "unknown", "unknown", "unknown")
        });

}

const observer = new MutationObserver(() => performScan(false));
observer.observe(document.body, { childList: true, subtree: true });

chrome.runtime.onMessage.addListener(msg => {
    if (msg.type === "TRIGGER_SCAN") performScan(true);
});
