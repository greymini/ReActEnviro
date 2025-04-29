const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Start the agent with a goal
 * @param {string} goal - The goal for the agent
 * @param {Object} context - Additional context for the agent
 * @returns {Promise} Promise resolving to the response data
 */
export const startAgent = async (goal, context = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ goal, context }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to start agent');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error starting agent:', error);
        throw error;
    }
};

/**
 * Stop the agent
 * @returns {Promise} Promise resolving to the response data
 */
export const stopAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/stop`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to stop agent');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error stopping agent:', error);
        throw error;
    }
};

/**
 * Reset the agent
 * @returns {Promise} Promise resolving to the response data
 */
export const resetAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/reset`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to reset agent');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error resetting agent:', error);
        throw error;
    }
};

/**
 * Get the current agent state
 * @returns {Promise} Promise resolving to the agent state
 */
export const getAgentState = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/state`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get agent state');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error getting agent state:', error);
        throw error;
    }
}; 