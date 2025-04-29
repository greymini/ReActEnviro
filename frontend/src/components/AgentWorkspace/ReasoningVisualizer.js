import React from 'react';
import './ReasoningVisualizer.css';

const ReasoningVisualizer = ({ thoughts, toolCalls, formatTime, containerRef }) => {
    // Find tool calls for a thought
    const getToolsForThought = (thoughtId) => {
        return toolCalls.filter(tc => tc.thought_id === thoughtId);
    };
    
    // Get tool names used in a thought
    const getToolNamesForThought = (thoughtId) => {
        const tools = getToolsForThought(thoughtId);
        return [...new Set(tools.map(t => t.tool_name))];
    };
    
    return (
        <div className="reasoning-visualizer">
            <div className="reasoning-header">
                <h2>Reasoning Process</h2>
                <div className="reasoning-stats">
                    <div className="stat">
                        <span className="stat-label">Thoughts:</span>
                        <span className="stat-value">{thoughts.length}</span>
                    </div>
                    <div className="stat">
                        <span className="stat-label">Tool Calls:</span>
                        <span className="stat-value">{toolCalls.length}</span>
                    </div>
                </div>
            </div>
            
            <div className="reasoning-container" ref={containerRef}>
                {thoughts.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">💭</div>
                        <div className="empty-message">No thoughts yet. Start the agent to see its reasoning process.</div>
                    </div>
                ) : (
                    thoughts.map((thought, index) => {
                        const toolsUsed = getToolNamesForThought(thought.id);
                        return (
                            <div key={thought.id} className="thought-card">
                                <div className="thought-number">#{index + 1}</div>
                                <div className="thought-header">
                                    <div className="thought-meta">
                                        <div className="thought-time">{formatTime(thought.timestamp)}</div>
                                    </div>
                                </div>
                                
                                <div className="thought-content">
                                    <div className="thought-bubble">
                                        <pre>{thought.content}</pre>
                                    </div>
                                </div>
                                
                                {toolsUsed.length > 0 && (
                                    <div className="tools-used">
                                        <span className="tools-used-label">Tools used:</span>
                                        <div className="tool-badges">
                                            {toolsUsed.map(tool => (
                                                <span key={tool} className="tool-badge">{tool}</span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                
                                {/* Display tool calls related to this thought */}
                                {getToolsForThought(thought.id).length > 0 && (
                                    <div className="tool-calls-container">
                                        {getToolsForThought(thought.id).map(toolCall => (
                                            <div key={toolCall.id} className={`tool-call-card ${toolCall.outputs ? 'completed' : toolCall.error ? 'error' : 'running'}`}>
                                                <div className="tool-call-header">
                                                    <div className="tool-icon">🔧</div>
                                                    <h4 className="tool-name">{toolCall.tool_name}</h4>
                                                    <div className="tool-status">
                                                        {toolCall.outputs && (
                                                            <span className="status-completed-badge">
                                                                <span>✓</span> completed
                                                            </span>
                                                        )}
                                                        {toolCall.error && (
                                                            <span className="status-error-badge">
                                                                <span>✗</span> failed
                                                            </span>
                                                        )}
                                                        {!toolCall.outputs && !toolCall.error && (
                                                            <span className="status-running-badge">
                                                                running
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                
                                                <div className="tool-call-content">
                                                    <div className="tool-section">
                                                        <h5>Inputs:</h5>
                                                        <pre>{JSON.stringify(toolCall.inputs, null, 2)}</pre>
                                                    </div>
                                                    
                                                    {toolCall.outputs && (
                                                        <div className="tool-section">
                                                            <h5>Outputs:</h5>
                                                            <pre>{JSON.stringify(toolCall.outputs, null, 2)}</pre>
                                                        </div>
                                                    )}
                                                    
                                                    {toolCall.error && (
                                                        <div className="tool-section tool-error">
                                                            <h5>Error:</h5>
                                                            <pre>{toolCall.error}</pre>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default ReasoningVisualizer; 