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
    // Detectar protocolo automáticamente
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;
    
    console.log('🔌 Conectando WebSocket a:', wsUrl); // Debug
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        addMessage("Conexión establecida con el chat IA.", "bot");
    };

    ws.onmessage = (event) => {
        typingIndicator.style.display = "none";
        document.querySelectorAll(".message.bot-thinking").forEach(e => e.remove());
        addMessage(event.data, "bot");
    };

    ws.onclose = (event) => {
        console.log('❌ WebSocket cerrado:', event.code, event.reason);
        addMessage("Conexión perdida. Reintentando...", "bot");
        setTimeout(connectWebSocket, 3000); // Aumenta el tiempo de reconexión
    };

    ws.onerror = (error) => {
        console.error('🚨 Error WebSocket:', error);
        addMessage("Error de WebSocket. Verificando conexión...", "bot");
        setTimeout(connectWebSocket, 5000);
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