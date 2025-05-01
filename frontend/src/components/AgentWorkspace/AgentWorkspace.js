import React, { useState, useEffect, useRef, useCallback } from 'react';
import './AgentWorkspace.css';
import GoalProgress from './GoalProgress';
import ToolExecutionPanel from './ToolExecutionPanel';
import ReasoningVisualizer from './ReasoningVisualizer';
import FinalReport from './FinalReport';
import { connectWebSocket, sendWebSocketCommand } from '../../services/websocket';

// Add a new UserInputModal component
function UserInputModal({ request, onSubmit, onCancel }) {
  const [inputValue, setInputValue] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(inputValue);
  };
  
  return (
    <div className="user-input-modal">
      <div className="user-input-modal-content">
        <h3>Agent Request</h3>
        <p>{request.prompt}</p>
        <form onSubmit={handleSubmit}>
          <textarea 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter your response..."
            rows={5}
          />
          <div className="user-input-actions">
            <button type="button" onClick={onCancel} className="cancel-button">
              Cancel
            </button>
            <button type="submit" className="submit-button">
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const AgentWorkspace = ({ initialContext = {} }) => {
    const [state, setState] = useState({
        goals: [],
        thoughts: [],
        toolCalls: [],
        status: 'idle',
        error: null
    });
    
    const [goal, setGoal] = useState('');
    const [loading, setLoading] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [showFinalReport, setShowFinalReport] = useState(false);
    const wsRef = useRef(null);
    const reasoningContainerRef = useRef(null);
    
    const [userInputRequest, setUserInputRequest] = useState(null);
    
    // Debug function to test WebSocket connection
    const testWebSocketConnection = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            console.log("Testing WebSocket connection with ping");
            sendWebSocketCommand(wsRef.current, { type: 'ping' });
        } else {
            console.error("WebSocket is not open for testing");
            setState(prev => ({
                ...prev,
                error: 'WebSocket connection is not available. Status: ' + 
                       (wsRef.current ? ['Connecting', 'Open', 'Closing', 'Closed'][wsRef.current.readyState] : 'Not initialized')
            }));
        }
    };
    
    // Format timestamp to readable time
    const formatTime = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp * 1000);
        return date.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: false
        });
    };
    
    // Handle WebSocket message
    const handleWebSocketMessage = useCallback((data) => {
        console.log('Handling WebSocket message in AgentWorkspace:', data);
        
        // Check if this is a connection status message
        if (data.type === 'connection_status') {
            setConnectionStatus(data.status);
            return;
        }
        
        // Handle the event coming from the backend
        if (data && data.event_type) {
            // Handle agent state updates inline
            const event = data;
            const { event_type, data: eventData } = event;
            
            console.log(`Handling event: ${event_type}`, eventData);
            
            switch (event_type) {
                case 'goal_set':
                    setState(prev => ({
                        ...prev,
                        goals: [...prev.goals, eventData.goal]
                    }));
                    break;
                    
                case 'thought_added':
                    setState(prev => ({
                        ...prev,
                        thoughts: [...prev.thoughts, eventData.thought]
                    }));
                    // Auto-scroll to the latest thought
                    setTimeout(() => {
                        if (reasoningContainerRef.current) {
                            reasoningContainerRef.current.scrollTop = reasoningContainerRef.current.scrollHeight;
                        }
                    }, 100);
                    break;
                    
                case 'tool_started':
                    const newToolCall = eventData.tool_call;
                    setState(prev => ({
                        ...prev,
                        toolCalls: [...prev.toolCalls, newToolCall]
                    }));
                    break;
                    
                case 'tool_completed':
                    setState(prev => ({
                        ...prev,
                        toolCalls: prev.toolCalls.map(tc => 
                            tc.id === eventData.tool_call_id 
                                ? { ...tc, outputs: eventData.outputs, end_time: Date.now() / 1000 }
                                : tc
                        )
                    }));
                    break;
                    
                case 'tool_failed':
                    setState(prev => ({
                        ...prev,
                        toolCalls: prev.toolCalls.map(tc => 
                            tc.id === eventData.tool_call_id 
                                ? { ...tc, error: eventData.error, end_time: Date.now() / 1000 }
                                : tc
                        )
                    }));
                    break;
                    
                case 'status_changed':
                    setLoading(eventData.status === 'thinking' || eventData.status === 'executing-tool');
                    setState(prev => ({
                        ...prev,
                        status: eventData.status
                    }));
                    
                    // When the agent completes, show the final report
                    if (eventData.status === 'completed') {
                        setShowFinalReport(true);
                    }
                    break;
                    
                case 'error':
                    setState(prev => ({
                        ...prev,
                        error: eventData.error
                    }));
                    break;
                    
                case 'goal_completed':
                    setState(prev => ({
                        ...prev,
                        goals: prev.goals.map(g => 
                            g.id === eventData.goal_id 
                                ? { ...g, completed: true }
                                : g
                        )
                    }));
                    break;
                    
                case 'state_reset':
                    setState({
                        goals: [],
                        thoughts: [],
                        toolCalls: [],
                        status: 'idle',
                        error: null
                    });
                    setGoal('');
                    setShowFinalReport(false);
                    break;
                    
                case 'user_input_request':
                    setUserInputRequest(eventData.request);
                    break;
                    
                default:
                    console.log(`Unknown event type: ${event_type}`);
            }
        }
    }, []);
    
    // Connect to WebSocket on component mount
    useEffect(() => {
        // Connect to WebSocket with callback
        try {
            setConnectionStatus('connecting');
            const ws = connectWebSocket(handleWebSocketMessage);
            
            ws.onopen = () => {
                setConnectionStatus('connected');
                console.log('WebSocket connected');
            };
            
            ws.onclose = () => {
                setConnectionStatus('disconnected');
                console.log('WebSocket disconnected');
            };
            
            ws.onerror = (error) => {
                setConnectionStatus('error');
                console.error('WebSocket error:', error);
                setState(prev => ({
                    ...prev,
                    error: 'Connection error. Please refresh the page and try again.'
                }));
            };
            
            wsRef.current = ws;
            
            // Clean up on unmount
            return () => {
                if (wsRef.current) {
                    wsRef.current.close();
                }
            };
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
            setConnectionStatus('error');
            setState(prev => ({
                ...prev,
                error: 'Failed to connect to server. Please refresh the page and try again.'
            }));
        }
    }, [handleWebSocketMessage]);
    
    // Toggle final report visibility
    const toggleFinalReport = () => {
        setShowFinalReport(!showFinalReport);
    };
    
    // Handle goal submission
    const handleGoalSubmit = (e) => {
        e.preventDefault();
        
        if (!goal.trim()) {
            setState(prev => ({
                ...prev,
                error: 'Please enter a goal for the agent'
            }));
            return;
        }
        
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            // Reset any previous errors
            setState(prev => ({
                ...prev,
                error: null
            }));
            
            sendWebSocketCommand(wsRef.current, {
                type: 'start',
                goal: goal,
                context: initialContext
            });
        } else {
            setState(prev => ({
                ...prev,
                error: 'WebSocket connection not available. Please refresh the page and try again.'
            }));
        }
    };
    
    // Handle stopping the agent
    const handleStopAgent = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            sendWebSocketCommand(wsRef.current, {
                type: 'stop'
            });
        }
    };
    
    // Handle resetting the agent
    const handleResetAgent = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            sendWebSocketCommand(wsRef.current, {
                type: 'reset'
            });
        } else {
            setState(prev => ({
                ...prev,
                error: 'WebSocket connection not available. Please refresh the page and try again.'
            }));
        }
    };
    
    // Generate a complete report from the agent's thoughts and tool calls
    const getFinalReport = () => {
        if (state.thoughts.length === 0 || state.goals.length === 0) {
            return null;
        }
        
        // Find if any goal is completed
        const completedGoal = state.goals.find(g => g.completed);
        if (!completedGoal) {
            return null;
        }
        
        // Get all thoughts to analyze
        const allThoughts = state.thoughts.map(t => t.content).join('\n\n');
        
        // Extract sections from thoughts
        const executiveSummary = extractSection(allThoughts, 'summary', 'executive summary', 'overview');
        const findings = extractSection(allThoughts, 'findings', 'key findings', 'assessment findings');
        const impacts = extractSection(allThoughts, 'impacts', 'environmental impacts', 'potential impacts');
        const mitigationMeasures = extractSection(allThoughts, 'mitigation', 'mitigation measures', 'recommended mitigation');
        const recommendations = extractSection(allThoughts, 'recommendations', 'recommended actions', 'proposed recommendations');
        const compliance = extractSection(allThoughts, 'compliance', 'regulatory compliance', 'regulations');
        
        // Get tool results categorized by assessment type
        const toolResults = state.toolCalls
            .filter(t => t.outputs)
            .reduce((acc, tool) => {
                const category = categorizeToolCall(tool);
                if (!acc[category]) {
                    acc[category] = [];
                }
                acc[category].push({
                    tool: formatToolName(tool.tool_name),
                    inputs: tool.inputs,
                    results: tool.outputs,
                    timestamp: tool.start_time
                });
                return acc;
            }, {});
        
        return {
            title: "Environmental Impact Assessment Report",
            goal: completedGoal.description,
            executiveSummary: executiveSummary || "No executive summary available.",
            findings: findings || "No specific findings available.",
            impacts: impacts || "No impact analysis available.",
            mitigationMeasures: mitigationMeasures || "No mitigation measures specified.",
            recommendations: recommendations || "No recommendations available.",
            compliance: compliance || "No compliance information available.",
            toolResults: toolResults,
            timestamp: Date.now()
        };
    };
    
    // Helper function to extract sections from text
    const extractSection = (text, ...sectionKeywords) => {
        // Look for sections that might contain the keywords
        const paragraphs = text.split('\n\n');
        
        // First try to find paragraphs that explicitly start with the keywords
        for (const keyword of sectionKeywords) {
            const regex = new RegExp(`(?:^|\\n)((?:${keyword}|${keyword.toUpperCase()})[:\\s].{10,})`, 'i');
            const match = text.match(regex);
            if (match && match[1]) {
                // If found, return the matching paragraph and potentially the next one
                const startIndex = paragraphs.findIndex(p => p.includes(match[1].substring(0, 30)));
                if (startIndex !== -1 && startIndex < paragraphs.length - 1) {
                    return paragraphs.slice(startIndex, startIndex + 2).join('\n\n');
                }
                return match[1];
            }
        }
        
        // If no explicit section found, look for paragraphs containing the keywords
        for (const keyword of sectionKeywords) {
            const relevantParagraphs = paragraphs.filter(p => 
                p.toLowerCase().includes(keyword.toLowerCase()) && p.length > 50);
            
            if (relevantParagraphs.length > 0) {
                return relevantParagraphs.join('\n\n');
            }
        }
        
        // If no section found, return a relevant portion of the text
        if (text.length > 200) {
            return text.substring(0, 500) + "...";
        }
        
        return null;
    };
    
    // Helper function to categorize tool calls
    const categorizeToolCall = (toolCall) => {
        const toolName = toolCall.tool_name.toLowerCase();
        const inputStr = JSON.stringify(toolCall.inputs).toLowerCase();
        
        if (toolName.includes('wetland') || inputStr.includes('wetland')) {
            return 'Wetland Assessment';
        } else if (toolName.includes('species') || toolName.includes('biological') || 
                   inputStr.includes('species') || inputStr.includes('biological')) {
            return 'Biological Assessment';
        } else if (toolName.includes('habitat') || inputStr.includes('habitat')) {
            return 'Habitat Evaluation';
        } else if (toolName.includes('water') || inputStr.includes('water')) {
            return 'Water Resources';
        } else if (toolName.includes('air') || inputStr.includes('air')) {
            return 'Air Quality';
        } else if (toolName.includes('noise') || inputStr.includes('noise')) {
            return 'Noise Assessment';
        } else if (toolName.includes('social') || inputStr.includes('social') || 
                   toolName.includes('community') || inputStr.includes('community')) {
            return 'Social Impact';
        } else if (toolName.includes('traffic') || inputStr.includes('traffic')) {
            return 'Traffic Analysis';
        } else if (toolName.includes('economic') || inputStr.includes('economic')) {
            return 'Economic Analysis';
        } else {
            return 'General Assessment';
        }
    };
    
    // Helper function to format tool names for readability
    const formatToolName = (name) => {
        if (!name) return 'Unknown Tool';
        
        // Remove underscores and convert to title case
        return name
            .replace(/_/g, ' ')
            .replace(/([a-z])([A-Z])/g, '$1 $2')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    };
    
    // Add handler for user input
    const handleUserInputSubmit = (inputValue) => {
        if (userInputRequest && wsRef.current) {
            sendWebSocketCommand(wsRef.current, {
                type: 'user_input',
                requestId: userInputRequest.id,
                data: inputValue
            });
            setUserInputRequest(null);
        }
    };
    
    const handleUserInputCancel = () => {
        // Send stop signal to the agent
        if (wsRef.current) {
            sendWebSocketCommand(wsRef.current, { type: 'stop' });
        }
        setUserInputRequest(null);
    };
    
    return (
        <div className="agent-workspace">
            <header className="workspace-header">
                <h1>AI Agent Reasoning Process</h1>
                <div className="connection-status">
                    <span className={`status-indicator ${connectionStatus}`}></span>
                    {connectionStatus === 'connected' ? 'Connected' : 
                     connectionStatus === 'connecting' ? 'Connecting...' : 
                     connectionStatus === 'error' ? 'Connection Error' : 'Disconnected'}
                </div>
                <form className="agent-controls" onSubmit={handleGoalSubmit}>
                    <input 
                        type="text" 
                        placeholder="Enter goal for the agent..." 
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        disabled={state.status !== 'idle'}
                        className="goal-input"
                    />
                    <div className="control-buttons">
                        <button 
                            type="submit"
                            disabled={state.status !== 'idle' || !goal.trim()}
                            className="start-button"
                        >
                            Start
                        </button>
                        <button 
                            type="button"
                            onClick={handleStopAgent}
                            disabled={!['thinking', 'executing-tool'].includes(state.status)}
                            className="stop-button"
                        >
                            Stop
                        </button>
                        <button 
                            type="button"
                            onClick={handleResetAgent}
                            disabled={state.status === 'thinking' || state.status === 'executing-tool'}
                            className="reset-button"
                        >
                            Reset
                        </button>
                    </div>
                </form>
                <div className="agent-status">
                    <div className="status-info">
                        <span>Status:</span> 
                        <span className={`status-${state.status}`}>
                            {state.status === 'idle' ? 'Ready' : 
                             state.status === 'thinking' ? 'Thinking...' : 
                             state.status === 'executing-tool' ? 'Executing Tool...' : 
                             state.status === 'completed' ? 'Completed' : 
                             state.status === 'failed' ? 'Failed' : state.status}
                        </span>
                        {loading && <div className="loading-spinner"></div>}
                        
                        {state.status === 'completed' && (
                            <button 
                                className="view-report-button"
                                onClick={toggleFinalReport}
                            >
                                {showFinalReport ? 'Hide Report' : 'View Final Report'}
                            </button>
                        )}
                        
                        {/* Add debug button for testing */}
                        <button 
                            className="debug-button"
                            onClick={testWebSocketConnection}
                            style={{ marginLeft: '10px', backgroundColor: '#333', color: 'white', padding: '5px 10px' }}
                        >
                            Test Connection
                        </button>
                    </div>
                    {state.error && (
                        <div className="error-message">
                            <div className="error-icon">!</div>
                            <div className="error-text">{state.error}</div>
                        </div>
                    )}
                </div>
            </header>
            
            {showFinalReport && (
                <FinalReport 
                    report={getFinalReport()} 
                    onClose={() => setShowFinalReport(false)}
                />
            )}
            
            <div className={`workspace-content ${showFinalReport ? 'hidden' : ''}`}>
                <div className="workspace-main">
                    <ReasoningVisualizer 
                        thoughts={state.thoughts}
                        toolCalls={state.toolCalls}
                        formatTime={formatTime}
                        containerRef={reasoningContainerRef}
                    />
                </div>
                
                <div className="workspace-sidebar">
                    <GoalProgress goals={state.goals} />
                    <ToolExecutionPanel toolCalls={state.toolCalls} />
                </div>
            </div>
            
            {userInputRequest && (
                <UserInputModal
                    request={userInputRequest}
                    onSubmit={handleUserInputSubmit}
                    onCancel={handleUserInputCancel}
                />
            )}
        </div>
    );
};

export default AgentWorkspace; 