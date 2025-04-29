/**
 * Establishes a connection to the WebSocket server.
 * @param {Function} onEventCallback - Callback function for WebSocket events
 * @returns {WebSocket} The WebSocket connection
 */
export const connectWebSocket = (onEventCallback) => {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/agent/ws';
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connection established successfully');
    };
    
    ws.onmessage = (event) => {
        try {
            console.log('Raw WebSocket message received:', event.data);
            const data = JSON.parse(event.data);
            console.log('Parsed WebSocket message:', data);
            
            // If callback is provided, call it with the event data
            if (onEventCallback && typeof onEventCallback === 'function') {
                onEventCallback(data);
            }
        } catch (error) {
            console.error('Error processing WebSocket message:', error, 'Raw data:', event.data);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = (event) => {
        console.log(`WebSocket connection closed with code ${event.code}. Reason: ${event.reason}`);
        // Could implement reconnection logic here if needed
    };
    
    return ws;
};

/**
 * Sends a command to the WebSocket server.
 * @param {WebSocket} ws - The WebSocket connection
 * @param {Object} command - The command to send
 */
export const sendWebSocketCommand = (ws, command) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const commandStr = JSON.stringify(command);
        console.log(`Sending WebSocket command: ${commandStr}`);
        ws.send(commandStr);
    } else {
        const readyStateText = ws ? 
            ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][ws.readyState] : 'NULL';
        console.error(`WebSocket is not in OPEN state. Current state: ${readyStateText}`);
    }
}; 