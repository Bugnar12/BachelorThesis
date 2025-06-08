document.getElementById("analyzeBtn").addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript(
        {
            target: { tabId: tab.id },
            func: extractEmailData,
        },
        (results) => {
            const resultEl = document.getElementById("result");

            if (chrome.runtime.lastError || !results || !results[0].result) {
                resultEl.textContent = "Could not extract email.";
                return;
            }

            const { subject, sender, body } = results[0].result;

            resultEl.innerText = `Analyzing...\n\nSubject: ${subject || "N/A"}\nSender: ${sender || "N/A"}`;
            // 🔁 Send to Flask backend for phishing prediction
            fetch("https://bachelorthesis-production-8acf.up.railway.app/emails/predict/email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ subject, sender, body }),
            })
                .then((res) => res.json())
                .then((data) => {
                    resultEl.innerText =
                        `Verdict: ${data.verdict || "N/A"}\n` +
                        `Text Analysis: ${data.text_prediction || "N/A"}\n` +
                        `URL Analysis: ${data.url_prediction || "N/A"}\n` +
                        `VT Analysis: ${data.vt_prediction || "N/A"}`;
                })
                .catch((err) => {
                    console.error(err);
                    resultEl.innerText = "Error contacting backend. Ensure the server is up&running.";
                });
        }
    );
});

function extractEmailData() {
    const subjectNode = document.querySelector('h2[data-legacy-thread-id]');
    const senderNode = document.querySelector('.gD');
    const bodyContainer = document.querySelector('div.a3s');

    let body = '';
    if (bodyContainer) {
        const span = bodyContainer.querySelector('span');
        if (span) {
            body = span.innerText;
        } else {
            body = bodyContainer.innerHTML;
        }
    }

    const subject = subjectNode ? subjectNode.innerText : null;
    const sender = senderNode ? senderNode.getAttribute('email') || senderNode.innerText : null;

    return { subject, sender, body };
}
