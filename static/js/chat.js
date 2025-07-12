document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatWindow = document.getElementById("chat-window");
    const typingIndicator = document.getElementById("typing-indicator");
    let ws;
    let sessionId = localStorage.getItem("session_id") || Math.random().toString(36).slice(2);

    function addMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message " + sender;
        const bubble = document.createElement("div");
        bubble.className = "bubble " + sender;
        bubble.innerHTML = text.replace(/\n/g, "<br>");
        msgDiv.appendChild(bubble);
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function showBotThinking() {
        document.querySelectorAll(".message.bot-thinking").forEach(e => e.remove());
        const msgDiv = document.createElement("div");
        msgDiv.className = "message bot-thinking";
        const bubble = document.createElement("div");
        bubble.className = "bubble bot";
        bubble.textContent = "Consultando datos...";
        msgDiv.appendChild(bubble);
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function connectWebSocket() {
        ws = new WebSocket(`ws://${window.location.host}/ws/${sessionId}`);

        ws.onopen = () => {
            addMessage("Conexión establecida con el chat IA.", "bot");
        };

        ws.onmessage = (event) => {
            typingIndicator.style.display = "none";
            document.querySelectorAll(".message.bot-thinking").forEach(e => e.remove());
            addMessage(event.data, "bot");
        };

        ws.onclose = () => {
            addMessage("Conexión perdida. Reintentando...", "bot");
            setTimeout(connectWebSocket, 2000); // Reconexión automática
        };

        ws.onerror = () => {
            addMessage("Error de WebSocket.", "bot");
            ws.close();
        };
    }

    connectWebSocket();

    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const userMsg = chatInput.value.trim();
        if (!userMsg || ws.readyState !== WebSocket.OPEN) return;
        addMessage(userMsg, "user");
        chatInput.value = "";
        typingIndicator.style.display = "block";
        showBotThinking();
        ws.send(userMsg);
    });
});