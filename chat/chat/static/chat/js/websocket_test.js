global.fetch = jest.fn();
document.querySelector = jest.fn();


require('./websocket');

describe('WebSocket Chat Tests', () => {
    let socket;
    const groupId = '1234';
    const websocketurl = `ws://localhost/ws/chat/${groupId}/`;

    const logEventMock = jest.fn();
    global.logEvent = logEventMock;

    global.WebSocket = jest.fn().mockImplementation(() => {
        return {
            readyState: WebSocket.CLOSED,
            send: jest.fn(),
            onmessage: null,
            onerror: null,
            onclose: null,
            onopen: null,
        };
    });

    beforeEach(() => {
        logEventMock.mockClear();
        WebSocket.mockClear();
    });

    test('WebSocket connection should establish and retry on failure', () => {
        const mockOnOpen = jest.fn();
        const mockOnClose = jest.fn();

        const socketInstance = new WebSocket(websocketurl);
        socketInstance.onopen = mockOnOpen;
        socketInstance.onclose = mockOnClose;

        connectToServer();

        expect(WebSocket).toHaveBeenCalledTimes(1);
        expect(socketInstance.onopen).toBeDefined();

        socketInstance.readyState = WebSocket.OPEN;
        socketInstance.onopen();
        expect(mockOnOpen).toHaveBeenCalled();

        socketInstance.readyState = WebSocket.CLOSED;
        socketInstance.onclose();
        expect(mockOnClose).toHaveBeenCalled();
        expect(logEventMock).toHaveBeenCalledWith("info", "WebSocket disconnected", {websocketurl});
    });

    test('Message is sent through WebSocket when input is submitted', () => {
        const socketInstance = new WebSocket(websocketurl);
        const mockSend = jest.fn();
        socketInstance.send = mockSend;

        const submitEvent = {
            preventDefault: jest.fn(),
            target: {
                message: {value: 'Test message'}
            }
        };
        document.querySelector = jest.fn().mockReturnValue({
            addEventListener: jest.fn().mockImplementation((event, handler) => {
                if (event === 'submit') handler(submitEvent);
            }),
        });

        socket = socketInstance;
        document.querySelector(".message-input-container").addEventListener('submit', (e) => {
            e.preventDefault();
            socket.send(JSON.stringify({message: e.target.message.value}));
        });

        expect(mockSend).toHaveBeenCalledWith(JSON.stringify({message: 'Test message'}));
        expect(logEventMock).toHaveBeenCalledWith("info", "Message sent", {message: 'Test message'});
    });

    test('Received message is appended to the chat', () => {
        const messageData = {
            content: 'Hello World',
            username: 'user1',
            created_date: '2024-11-25',
            profile_picture: 'http://example.com/img.jpg',
            active_count: 3,
            owner: '5678',
        };

        const socketInstance = new WebSocket(websocketurl);
        const mockAppendMessage = jest.fn();

        socketInstance.onmessage({data: JSON.stringify(messageData)});

        expect(mockAppendMessage).toHaveBeenCalledWith(messageData, true);
        expect(logEventMock).toHaveBeenCalledWith("info", "Message appended", {
            content: 'Hello World',
            username: 'user1',
            owner: true
        });
    });

    test('WebSocket error handler should log errors', () => {
        const socketInstance = new WebSocket(websocketurl);
        socketInstance.onerror(new Error('WebSocket error occurred'));
        expect(logEventMock).toHaveBeenCalledWith("error", "WebSocket error occurred", {error: 'Error: WebSocket error occurred'});
    });

    test('WebSocket should reconnect on close', () => {
        const mockReconnect = jest.fn();
        const socketInstance = new WebSocket(websocketurl);
        socketInstance.onclose = mockReconnect;

        socketInstance.onclose();
        expect(mockReconnect).toHaveBeenCalled();
        expect(logEventMock).toHaveBeenCalledWith("info", "WebSocket disconnected", {websocketurl});
    });
});
