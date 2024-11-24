global.fetch = jest.fn();
document.querySelector = jest.fn();

require('./index')

describe("Chat functionality", () => {
    beforeEach(() => {
        fetch.mockReset();
        document.querySelector.mockReset();
    });

    it("should log events correctly", async () => {
        fetch.mockResolvedValueOnce({ status: 200 });

        const logMessage = "Test log message";
        const logServerUrl = "http://mock-api-url.com/log";
        const logEntry = {
            type: "INFO",
            message: logMessage,
            additionalData: {},
            timestamp: expect.any(String),
            userId: "mockUserId",
        };

        document.querySelector.mockReturnValueOnce({ value: "mockUserId" });
        await logEvent("INFO", logMessage);

        expect(fetch).toHaveBeenCalledWith(logServerUrl, expect.objectContaining({
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(logEntry),
        }));

        expect(fetch).toHaveBeenCalledTimes(1);
    });

    it("should handle fetch errors gracefully", async () => {
        fetch.mockRejectedValueOnce(new Error("Network error"));
        document.querySelector.mockReturnValueOnce({ value: "mockUserId" });

        const logMessage = "Test log error message";
        await logEvent("ERROR", logMessage);
        const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        expect(consoleErrorSpy).toHaveBeenCalledWith(expect.any(Error));
        consoleErrorSpy.mockRestore();
    });

    it("should load chat rooms and display them", async () => {
        const mockResponseData = [
            { topic: "Test Chat", last_message: "Hello", last_updated: "2024-11-24", get_absolute_url: "/chat/1", dp: "/images/profile1.jpg" }
        ];

        fetch.mockResolvedValueOnce({
            status: 200,
            json: async () => mockResponseData,
        });

        document.querySelector.mockReturnValueOnce({
            innerHTML: ""
        });

        const parent = document.createElement("div");
        parent.classList.add("conversation-lists");
        document.body.appendChild(parent);

        await (async () => {
            const data = await getChatRooms();
            const parent = document.querySelector(".conversation-lists");
            const chatListElements = data.map((item) => conversationListHtml(item));
            parent.innerHTML = chatListElements.join("");
        })();

        const conversation = document.querySelector(".conversation");
        expect(conversation).not.toBeNull();
        expect(conversation.querySelector(".group-name").textContent).toBe("Test Chat");
    });
});
