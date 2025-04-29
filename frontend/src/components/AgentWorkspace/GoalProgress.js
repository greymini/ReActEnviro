import React from 'react';
import './GoalProgress.css';

const GoalProgress = ({ goals }) => {
    return (
        <div className="goal-progress">
            <div className="panel-header">
                <h2>
                    <span className="icon">🎯</span>
                    Goals
                </h2>
            </div>
            
            <div className="goals-container">
                {goals.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">🎯</div>
                        <div className="empty-message">No goals set yet</div>
                    </div>
                ) : (
                    <ul className="goals-list">
                        {goals.map(goal => (
                            <li key={goal.id} className={`goal-item ${goal.completed ? 'completed' : ''}`}>
                                <div className="goal-status">
                                    {goal.completed ? (
                                        <span className="completed-icon">✓</span>
                                    ) : (
                                        <span className="pending-icon"></span>
                                    )}
                                </div>
                                <div className="goal-content">
                                    <div className="goal-description">{goal.description}</div>
                                    <div className="goal-meta">
                                        {goal.completed ? (
                                            <span className="goal-status-text completed">Completed</span>
                                        ) : (
                                            <span className="goal-status-text pending">In Progress</span>
                                        )}
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default GoalProgress; 