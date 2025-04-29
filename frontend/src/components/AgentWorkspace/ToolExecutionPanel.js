import React, { useState } from 'react';
import './ToolExecutionPanel.css';

const ToolExecutionPanel = ({ toolCalls }) => {
    const [expandedTool, setExpandedTool] = useState(null);
    
    // Group tool calls by tool name
    const groupToolsByType = () => {
        const groups = {};
        toolCalls.forEach(tool => {
            if (!groups[tool.tool_name]) {
                groups[tool.tool_name] = [];
            }
            groups[tool.tool_name].push(tool);
        });
        return groups;
    };
    
    const toolGroups = groupToolsByType();
    
    // Get stats for tool executions
    const getToolStats = () => {
        const totalTools = toolCalls.length;
        const completedTools = toolCalls.filter(t => t.outputs).length;
        const failedTools = toolCalls.filter(t => t.error).length;
        const runningTools = totalTools - completedTools - failedTools;
        
        return { totalTools, completedTools, failedTools, runningTools };
    };
    
    const stats = getToolStats();
    
    // Toggle tool expansion to show details
    const toggleToolExpansion = (toolId) => {
        if (expandedTool === toolId) {
            setExpandedTool(null);
        } else {
            setExpandedTool(toolId);
        }
    };
    
    // Format tool name to be more readable
    const formatToolName = (name) => {
        return name
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };
    
    // Format parameter name to be more readable
    const formatParamName = (name) => {
        return name
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };
    
    return (
        <div className="tool-execution-panel">
            <div className="panel-header">
                <h2>
                    <span className="icon">🔧</span>
                    Tool Executions
                </h2>
            </div>
            
            <div className="tool-stats">
                <div className="stat total">
                    <div className="stat-value">{stats.totalTools}</div>
                    <div className="stat-label">Total</div>
                </div>
                <div className="stat completed">
                    <div className="stat-value">{stats.completedTools}</div>
                    <div className="stat-label">Completed</div>
                </div>
                <div className="stat failed">
                    <div className="stat-value">{stats.failedTools}</div>
                    <div className="stat-label">Failed</div>
                </div>
                {stats.runningTools > 0 && (
                    <div className="stat running">
                        <div className="stat-value">{stats.runningTools}</div>
                        <div className="stat-label">Running</div>
                    </div>
                )}
            </div>
            
            <div className="tools-container">
                {toolCalls.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">🔧</div>
                        <div className="empty-message">No tools executed yet</div>
                    </div>
                ) : (
                    <div className="tool-groups">
                        {Object.entries(toolGroups).map(([toolName, tools]) => (
                            <div key={toolName} className="tool-group">
                                <div className="tool-group-header">
                                    <h3 className="tool-name">{formatToolName(toolName)}</h3>
                                    <div className="tool-count">{tools.length}</div>
                                </div>
                                <ul className="tool-list">
                                    {tools.map(tool => (
                                        <li 
                                            key={tool.id} 
                                            className={`tool-item ${tool.outputs ? 'completed' : tool.error ? 'error' : 'running'} ${expandedTool === tool.id ? 'expanded' : ''}`}
                                            onClick={() => toggleToolExpansion(tool.id)}
                                        >
                                            <div className="tool-status-icon">
                                                {tool.outputs && <span className="status-icon completed">✓</span>}
                                                {tool.error && <span className="status-icon error">✗</span>}
                                                {!tool.outputs && !tool.error && <span className="status-icon running"></span>}
                                            </div>
                                            <div className="tool-execution-info">
                                                <div className="tool-title">
                                                    <span className="execution-time">
                                                        {tool.end_time ? new Date(tool.end_time * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) : 'Running...'}
                                                    </span>
                                                    <span className="expand-indicator">{expandedTool === tool.id ? '▼' : '▶'}</span>
                                                </div>
                                                <div className="tool-parameters">
                                                    {Object.entries(tool.inputs).slice(0, 2).map(([key, value]) => (
                                                        <span key={key} className="tool-param">
                                                            {formatParamName(key)}: {renderParamValue(value)}
                                                        </span>
                                                    ))}
                                                    {Object.keys(tool.inputs).length > 2 && (
                                                        <span className="more-params">+{Object.keys(tool.inputs).length - 2} more</span>
                                                    )}
                                                </div>
                                                
                                                {/* Expanded view with all parameters and results */}
                                                {expandedTool === tool.id && (
                                                    <div className="tool-details">
                                                        <div className="tool-params-detail">
                                                            <h5>Parameters</h5>
                                                            <table className="params-table">
                                                                <tbody>
                                                                    {Object.entries(tool.inputs).map(([key, value]) => (
                                                                        <tr key={key}>
                                                                            <td className="param-key">{formatParamName(key)}</td>
                                                                            <td className="param-value">{renderParamValue(value, true)}</td>
                                                                        </tr>
                                                                    ))}
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                        
                                                        {tool.outputs && (
                                                            <div className="tool-result-detail">
                                                                <h5>Results</h5>
                                                                <pre className="result-data">{JSON.stringify(tool.outputs, null, 2)}</pre>
                                                            </div>
                                                        )}
                                                        
                                                        {tool.error && (
                                                            <div className="tool-error-detail">
                                                                <h5>Error</h5>
                                                                <pre className="error-data">{tool.error}</pre>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

// Helper function to render parameter values in a readable way
const renderParamValue = (value, detailed = false) => {
    if (value === null || value === undefined) {
        return 'null';
    }
    
    if (Array.isArray(value)) {
        if (detailed) {
            return JSON.stringify(value, null, 2);
        }
        return value.length > 0 ? `[${value.length} items]` : '[]';
    }
    
    if (typeof value === 'object') {
        if (detailed) {
            return JSON.stringify(value, null, 2);
        }
        const keys = Object.keys(value);
        return keys.length > 0 ? `{${keys.join(', ')}}` : '{}';
    }
    
    if (typeof value === 'string') {
        if (detailed) return value;
        return value.length > 30 ? value.substring(0, 27) + '...' : value;
    }
    
    return String(value);
};

export default ToolExecutionPanel; 