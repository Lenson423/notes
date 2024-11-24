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


async function sendLog(logMessage) {
    try {
        await fetch(logApiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ log: logMessage }),
        });
    } catch (error) {
        console.error("Ошибка при отправке лога:", error);
    }
}

function viewConversation(event) {
    const node = event;
    const path = node.getAttribute("data--href");
    sendLog(`Navigating to conversation path: ${path}`);
    if (window.location.pathname !== path) window.location = path;
}

function conversationListHtml(data) {
    const { topic, last_message, last_updated, get_absolute_url, dp } = data;
    const message_last_sent = last_message
        ? last_message.length > 45
            ? last_message.slice(0, 45) + "..."
            : last_message
        : "";
    return `
    <div class="conversation ${
        topic === chat_room_name && "active"
    }" role="link" data--href="${get_absolute_url}" onclick="viewConversation(this)">
        <div class="conversation-info">
            <img
                src="${dp}"
                alt="${topic} profile"
                class="profile-image"
            />
            <div>
                <h3 class="group-name">${topic}</h3>
                <div>${message_last_sent}</div>
            </div>
        </div>
        <span class="conversation-last-time">${last_updated ? last_updated : ""}</span>    
    </div>
    `;
}

const getChatRooms = async () => {
    try {
        const response = await fetch(roomListApiView);
        if (response.status !== 200) {
            sendLog(`Failed to fetch chat rooms: Status ${response.status}`);
            return [];
        }
        const data = await response.json();
        return data;
    } catch (error) {
        sendLog(`Error fetching chat rooms: ${error.message}`);
        return [];
    }
};

(async () => {
    try {
        const data = await getChatRooms();
        const parent = document.querySelector(".conversation-lists");
        const chatListElements = data.map((item) => conversationListHtml(item));
        parent.innerHTML = chatListElements.join("");
        const activeNode = document.querySelector(".conversation.active");
        if (activeNode) activeNode.scrollIntoView({ behavior: "smooth" });
        sendLog("Chat rooms loaded successfully");
    } catch (error) {
        sendLog(`Error in chat room initialization: ${error.message}`);
    }
})();

function scrollToBottom() {
    const node = document.querySelector(".msg:last-child");
    if (node) {
        node.scrollIntoView({ behavior: "smooth" });
        sendLog("Scrolled to the bottom of the chat");
    }
}
