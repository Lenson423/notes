global.fetch = jest.fn();
document.querySelector = jest.fn();


require('./messages');

describe("Chat Messages functionality", () => {
    beforeEach(() => {
        fetch.mockReset();
        document.querySelector.mockReset();
        global.scrollToBottom.mockReset();
    });

    it("should fetch messages successfully", async () => {
        const mockResponseData = {
            topic: "Test Topic",
            number_of_members: 10,
            active_members_count: 5,
            dp: "/images/group.jpg",
            members: [
                { username: "user1", profile_image: "/images/user1.jpg", active: true },
                { username: "user2", profile_image: "/images/user2.jpg", active: false },
            ],
            messages: [
                {
                    content: "Hello, world!",
                    owner_username: "user1",
                    is_owner: true,
                    user_profile_picture: "/images/user1.jpg",
                    time_created_string: "2024-11-24 12:00",
                },
            ],
        };

        fetch.mockResolvedValueOnce({
            status: 200,
            json: async () => mockResponseData,
        });

        document.querySelector.mockReturnValueOnce({
            innerHTML: "",
        });

        const roomId = 1;
        const data = await getMessages();
        expect(data).toEqual(mockResponseData);
        expect(logEvent).toHaveBeenCalledWith("info", "Successfully fetched messages", { roomId });

        const messagesHtmlElementStr = document.querySelector(".messages");
        expect(messagesHtmlElementStr.innerHTML).toContain("Hello, world!");

        expect(scrollToBottom).toHaveBeenCalled();
    });

    it("should handle fetch errors gracefully", async () => {
        fetch.mockRejectedValueOnce(new Error("Network error"));

        const roomId = 1;
        const data = await getMessages();

        expect(data).toEqual([]);

        expect(logEvent).toHaveBeenCalledWith("error", "Error while fetching messages", { roomId, error: "Network error" });
    });

    it("should update messages header correctly", () => {
        const topic = "Test Topic";
        const number_of_members = 10;
        const active_members = 5;
        const dp = "/images/group.jpg";

        document.querySelector.mockReturnValueOnce({
            innerHTML: "",
        });

        updateMessagesHeader(topic, number_of_members, active_members, dp);

        const messageSection = document.querySelector(".message-section-header");
        expect(messageSection.innerHTML).toContain(topic);
        expect(messageSection.innerHTML).toContain("10 Members");
        expect(messageSection.innerHTML).toContain("5 active members");
    });

    it("should update the members list", () => {
        const members = [
            { username: "user1", profile_image: "/images/user1.jpg", active: true },
            { username: "user2", profile_image: "/images/user2.jpg", active: false },
        ];

        document.querySelector.mockReturnValueOnce({
            innerHTML: "",
        });

        updateMembersList(members);

        const membersList = document.querySelector(".user-list");
        expect(membersList.innerHTML).toContain("user1");
        expect(membersList.innerHTML).toContain("active now");
        expect(membersList.innerHTML).toContain("user2");
        expect(membersList.innerHTML).not.toContain("active now");
    });

    it("should generate the correct message HTML", () => {
        const content = "Test message";
        const owner_username = "user1";
        const isOwner = true;
        const user_profile_picture = "/images/user1.jpg";
        const created_date = "2024-11-24";

        const messageHtml = getMessageHtmlText(content, owner_username, isOwner, user_profile_picture, created_date);

        expect(messageHtml).toContain(content);
        expect(messageHtml).toContain(owner_username);
        expect(messageHtml).toContain(user_profile_picture);
        expect(messageHtml).toContain(created_date);
    });

    it("should handle message display correctly", async () => {
        const mockResponseData = {
            topic: "Test Topic",
            number_of_members: 10,
            active_members_count: 5,
            dp: "/images/group.jpg",
            members: [
                { username: "user1", profile_image: "/images/user1.jpg", active: true },
                { username: "user2", profile_image: "/images/user2.jpg", active: false },
            ],
            messages: [
                {
                    content: "Hello, world!",
                    owner_username: "user1",
                    is_owner: true,
                    user_profile_picture: "/images/user1.jpg",
                    time_created_string: "2024-11-24 12:00",
                },
            ],
        };

        fetch.mockResolvedValueOnce({
            status: 200,
            json: async () => mockResponseData,
        });

        document.querySelector.mockReturnValueOnce({
            innerHTML: "",
        });

        await displayMessages();

        const messagesHtmlElementStr = document.querySelector(".messages");
        expect(messagesHtmlElementStr.innerHTML).toContain("Hello, world!");
        expect(scrollToBottom).toHaveBeenCalled();
    });
});

