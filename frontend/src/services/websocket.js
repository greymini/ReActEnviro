/**
 * Establishes a connection to the WebSocket server.
 * @param {Function} onMessageCallback - Callback function for WebSocket events
 * @returns {WebSocket} The WebSocket connection
 */
export const connectWebSocket = (onMessageCallback) => {
    // Always use localhost:8000 to connect to the backend, regardless of which port the frontend is on
    const wsUrl = 'ws://localhost:8000/ws/agent';
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000; // 3 seconds
    
    let socket = null;
    
    try {
        // Create a new WebSocket connection
        socket = new WebSocket(wsUrl);
        console.log("WebSocket instance created", socket);
    } catch (e) {
        console.error("Error creating WebSocket:", e);
        onMessageCallback({
            type: 'connection_status',
            status: 'error',
            error: `Failed to create WebSocket: ${e.message}`
        });
        return null;
    }

    const setupSocket = () => {
        // Set up event handlers
        socket.onopen = () => {
            console.log('WebSocket connection established');
            reconnectAttempts = 0; // Reset reconnect attempts on successful connection
            
            // Notify the UI that we're connected
            onMessageCallback({
                type: 'connection_status',
                status: 'connected'
            });
            
            // Send a test message to verify connection is working properly
            try {
                console.log("Sending test message to verify connection");
                socket.send(JSON.stringify({ type: 'ping' }));
            } catch (error) {
                console.error("Error sending test message:", error);
            }
        };

        socket.onmessage = (event) => {
            try {
                console.log('Raw WebSocket message received:', event.data);
                const data = JSON.parse(event.data);
                console.log('WebSocket message received:', data);
                
                // Add detailed logging to help debug
                console.log('WebSocket message event_type:', data.event_type);
                console.log('WebSocket message data content:', data.data);
                
                // Check for user input request
                if (data.type === 'state_update' && data.userInputRequest) {
                    onMessageCallback({
                        type: 'user_input_request',
                        request: data.userInputRequest
                    });
                }
                
                // Forward all other messages
                onMessageCallback(data);
            } catch (error) {
                console.error('Error processing WebSocket message:', error, 'Raw data:', event.data);
            }
        };

        socket.onclose = (event) => {
            console.log(`WebSocket connection closed with code ${event.code}. Reason: ${event.reason}`);
            console.log('Close event details:', event);
            
            // Notify the UI that we're disconnected
            onMessageCallback({
                type: 'connection_status',
                status: 'disconnected'
            });
            
            // Try to reconnect if not closing cleanly
            if (event.code !== 1000 && event.code !== 1001) {
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`);
                    
                    // Notify the UI that we're trying to reconnect
                    onMessageCallback({
                        type: 'connection_status',
                        status: 'reconnecting',
                        attempt: reconnectAttempts,
                        maxAttempts: maxReconnectAttempts
                    });
                    
                    setTimeout(() => {
                        socket = new WebSocket(wsUrl);
                        setupSocket();
                    }, reconnectDelay);
                } else {
                    console.error('Maximum reconnection attempts reached.');
                    
                    // Notify the UI that reconnection failed
                    onMessageCallback({
                        type: 'connection_status',
                        status: 'failed',
                        error: 'Maximum reconnection attempts reached.'
                    });
                }
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            console.log('WebSocket readyState:', socket.readyState);
            
            // Notify the UI of the error
            onMessageCallback({
                type: 'connection_status',
                status: 'error',
                error: 'Connection error'
            });
        };
    };
    
    setupSocket();
    return socket;
};

/**
 * Sends a command to the WebSocket server.
 * @param {WebSocket} socket - The WebSocket connection
 * @param {Object} command - The command to send
 */
export const sendWebSocketCommand = (socket, command) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log('Sending WebSocket command:', command);
        socket.send(JSON.stringify(command));
    } else {
        console.error('WebSocket is not open for sending commands.');
    }
}; 