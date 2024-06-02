document.addEventListener("DOMContentLoaded", function () {
    const clientId = Math.floor(Math.random() * 1000); // Gerar um ID de cliente aleatório
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);

    const messagesDiv = document.getElementById("messages");
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");

    websocket.onmessage = function (event) {
        const message = document.createElement("div");
        message.textContent = event.data;
        messagesDiv.appendChild(message);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll para o fundo
    };

    sendButton.addEventListener("click", function () {
        const message = messageInput.value;
        if (message) {
            websocket.send(message);
            messageInput.value = "";
        }
    });

    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendButton.click();
        }
    });
});
