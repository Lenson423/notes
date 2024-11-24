const logServerUrl = `25.31.176.32:8000/logs/`;

function logEvent(type, message, additionalData = {}) {
    const logEntry = {
        type,
        message,
        additionalData,
        timestamp: new Date().toISOString(),
        userId: document.querySelector("#id-user-id").value,
    };

    fetch(logServerUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(logEntry),
    }).catch(console.error);
}

// Global => ScrollToBottom, getMessagHtmlText, host

const wsprotocol = host === "https" ? "wss" : "ws";
const groupId = document.getElementById("group_id").value;
const websocketurl = `${wsprotocol}://${host}/ws/chat/${groupId}/`;
const userId = document.querySelector("#id-user-id").value;
const retryFrequency = 1600; // Unit -> milliseconds
let CONNECTED_TO_SERVER = false;
let socket;

function addAttributesToSocket(socket) {
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        logEvent("info", "Received message", { data });
        appendMessage(data, data.owner == userId);
    };

    socket.onerror = (e) => {
        logEvent("error", "WebSocket error occurred", { error: e });
        console.error("WebSocket error:", e);
    };

    socket.onclose = () => {
        logEvent("info", "WebSocket disconnected", { websocketurl });
        console.log("Disconnected");
        CONNECTED_TO_SERVER = false;
        connectToServer();
    };

    socket.onopen = () => {
        logEvent("info", "WebSocket connection established", { websocketurl });
        console.log("WebSocket is open");
    };
}

function makeConnection(action) {
    let chatSocket = new WebSocket(websocketurl);
    const connect = setInterval(() => {
        console.log("Connecting...");
        if (chatSocket.readyState === WebSocket.OPEN) {
            clearInterval(connect); // Успешное подключение
            logEvent("info", "WebSocket connected successfully", { websocketurl });
            action(chatSocket);
        } else if (chatSocket.readyState === WebSocket.CLOSED) {
            logEvent("warning", "WebSocket connection failed, retrying", {
                retryAfter: retryFrequency / 1000,
            });
            console.error(`Socket closed, retrying in ${retryFrequency / 1000}s`);
            chatSocket = new WebSocket(websocketurl); // Попытка снова подключиться
        }
    }, retryFrequency);
}

function connectToServer() {
    makeConnection((newSocket) => {
        addAttributesToSocket(newSocket);
        socket = newSocket;
        CONNECTED_TO_SERVER = true;
    });
}

function appendMessage(message, owner) {
    const { content, username, created_date, profile_picture, active_count } = message;
    const messageArea = document.querySelector(".messages");
    const messageHtmlText = getMessageHtmlText(
        content,
        username,
        owner,
        profile_picture,
        created_date
    );
    messageArea.innerHTML += messageHtmlText;
    document.getElementById("active-members-count").textContent = active_count - 1;
    scrollToBottom();
    logEvent("info", "Message appended", { content, username, owner });
}

document.querySelector(".message-input-container").addEventListener("submit", (e) => {
    e.preventDefault();
    if (!CONNECTED_TO_SERVER) {
        alert("Error sending message, check your network connection");
        logEvent("error", "Message sending failed, WebSocket disconnected");
        return;
    }
    const messageInputEl = e.target.message;
    const message = messageInputEl.value;
    if (message.length < 1) return;
    socket.send(JSON.stringify({ message: message }));
    logEvent("info", "Message sent", { message });
    messageInputEl.value = "";
});

connectToServer();
