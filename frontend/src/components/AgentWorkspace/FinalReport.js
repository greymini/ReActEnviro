import React from 'react';
import './FinalReport.css';

const FinalReport = ({ report, onClose }) => {
    if (!report) {
        return (
            <div className="final-report">
                <div className="report-header">
                    <h2>Final Report</h2>
                    <button className="close-button" onClick={onClose}>×</button>
                </div>
                <div className="report-content">
                    <div className="no-report">No report available yet.</div>
                </div>
            </div>
        );
    }

    // Format the report content for better readability
    const formatReportContent = (content) => {
        if (!content) return '';
        
        // Replace markdown-style headings with HTML
        let formattedContent = content
            .replace(/## (.*?)\n/g, '<h3>$1</h3>')
            .replace(/# (.*?)\n/g, '<h2>$1</h2>')
            .replace(/\n\n/g, '<br><br>');

        // Convert plain text into paragraphs
        const paragraphs = formattedContent.split('<br><br>');
        formattedContent = paragraphs
            .map(p => {
                if (p.startsWith('<h2>') || p.startsWith('<h3>')) {
                    return p;
                }
                return `<p>${p}</p>`;
            })
            .join('');

        return formattedContent;
    };

    // Format date and time for the report
    const formatDateTime = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="final-report">
            <div className="report-header">
                <h2>{report.title}</h2>
                <button className="close-button" onClick={onClose}>×</button>
            </div>
            
            <div className="report-content">
                <div className="goal-section">
                    <h3>Assessment Goal</h3>
                    <p>{report.goal}</p>
                    {report.timestamp && (
                        <div className="report-date">
                            Generated on: {formatDateTime(report.timestamp)}
                        </div>
                    )}
                </div>
                
                <div className="report-body">
                    <section className="report-section">
                        <h2>Executive Summary</h2>
                        <div dangerouslySetInnerHTML={{ 
                            __html: formatReportContent(report.executiveSummary) 
                        }} />
                    </section>
                    
                    <section className="report-section">
                        <h2>Key Findings</h2>
                        <div dangerouslySetInnerHTML={{ 
                            __html: formatReportContent(report.findings) 
                        }} />
                    </section>
                    
                    <section className="report-section">
                        <h2>Environmental Impacts</h2>
                        <div dangerouslySetInnerHTML={{ 
                            __html: formatReportContent(report.impacts) 
                        }} />
                    </section>
                    
                    <section className="report-section">
                        <h2>Mitigation Measures</h2>
                        <div dangerouslySetInnerHTML={{ 
                            __html: formatReportContent(report.mitigationMeasures) 
                        }} />
                    </section>
                    
                    <section className="report-section">
                        <h2>Recommendations</h2>
                        <div dangerouslySetInnerHTML={{ 
                            __html: formatReportContent(report.recommendations) 
                        }} />
                    </section>
                    
                    <section className="report-section">
                        <h2>Regulatory Compliance</h2>
                        <div dangerouslySetInnerHTML={{ 
                            __html: formatReportContent(report.compliance) 
                        }} />
                    </section>
                </div>
                
                <div className="tool-results-section">
                    <h2>Assessment Tools and Results</h2>
                    {Object.entries(report.toolResults).map(([category, tools]) => (
                        <div className="tool-category" key={category}>
                            <h3>{category}</h3>
                            <div className="tool-results-grid">
                                {tools.map((tool, index) => (
                                    <div className="tool-result-card" key={index}>
                                        <div className="tool-result-header">
                                            <h4>{tool.tool}</h4>
                                            {tool.timestamp && (
                                                <div className="tool-timestamp">
                                                    {new Date(tool.timestamp).toLocaleTimeString()}
                                                </div>
                                            )}
                                        </div>
                                        <div className="tool-params">
                                            <h5>Parameters</h5>
                                            <ul>
                                                {Object.entries(tool.inputs).map(([key, value]) => (
                                                    <li key={key}>
                                                        <span className="param-name">{formatParamName(key)}:</span> 
                                                        <span className="param-value">{formatParamValue(value)}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div className="tool-result-summary">
                                            <h5>Results Summary</h5>
                                            <p>{summarizeToolResults(tool.results)}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Format parameter names for better readability
const formatParamName = (name) => {
    if (!name) return '';
    return name
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
};

// Format parameter values for display
const formatParamValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
};

// Create a brief summary of tool results
const summarizeToolResults = (results) => {
    if (typeof results === 'string') {
        // If it's a string, return first 150 characters
        return results.length > 150 ? results.substring(0, 150) + '...' : results;
    } else if (typeof results === 'object' && results !== null) {
        // For objects, create a summary of key findings
        const keys = Object.keys(results);
        if (keys.length === 0) return 'No results';
        
        if (keys.includes('findings') || keys.includes('recommendations') || keys.includes('summary')) {
            // If the results have specific summary keys, use those
            const summaryKey = keys.find(k => ['findings', 'recommendations', 'summary'].includes(k));
            return results[summaryKey];
        }
        
        // Otherwise, list the keys that are present
        return `Results include: ${keys.join(', ')}`;
    }
    
    return 'Results unavailable';
};

export default FinalReport; 