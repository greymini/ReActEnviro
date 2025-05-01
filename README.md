# ReActEnviro - Environmental Impact Assessment AI Agent

![ReActEnviro Overview](https://raw.githubusercontent.com/greymini/ReActEnviro/main/EnviroReact%20Landing%20Page.png)

# Demo Video:
https://github.com/greymini/ReActEnviro/issues/1

## Overview

ReActEnviro is an advanced AI agent system designed to conduct comprehensive environmental impact assessments for proposed construction projects. The system leverages the ReAct (Reasoning and Acting) framework to provide thorough, transparent, and explainable environmental analyses in real-time.

## Key Features

- **ReAct Framework Implementation**: Combines reasoning and tool usage to perform comprehensive environmental assessments
- **Specialized Environmental Assessment Tools**: Includes tools for site analysis, regulatory compliance, air quality, hydrological assessment, and water quality assessment
- **Real-time Analysis**: Provides step-by-step insights into the agent's reasoning process and decision-making
- **Interactive Web Interface**: Visualizes the agent's thought process, tool calls, and final assessment report
- **Transparent Reasoning**: Allows users to follow the agent's analysis, including all considerations and sub-assessments

## System Architecture

The application follows a client-server architecture:

- **Backend**: FastAPI-based server implementing the ReAct agent
- **Frontend**: React application that visualizes the agent's reasoning process
- **Monitoring**: Prometheus and Grafana for system metrics (work in progress)

## Core Components

### Backend

- **ReAct Agent**: Implements the reasoning-acting loop for environmental assessment
- **Tool Orchestrator**: Manages specialized environmental assessment tools
- **LLM Service**: Interfaces with language models for reasoning capabilities
- **WebSocket Service**: Enables real-time communication with the frontend

### Frontend

- **Agent Workspace**: Main interface displaying the agent's reasoning process
- **Reasoning Visualizer**: Shows the agent's thoughts and tool calls in real-time
- **Tool Execution Panel**: Tracks tools being used by the agent
- **Final Report**: Generates a comprehensive environmental impact assessment report

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/greymini/ReActEnviro.git
   cd ReActEnviro
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Navigate to `http://localhost:3000` in your browser

## Usage

1. Enter an environmental assessment goal in the input field (e.g., "Conduct an environmental impact assessment for a proposed 3-story office building on a 1.5-acre site near a wetland area in Austin, TX")
2. Click the "Start" button to initiate the agent
3. Watch in real-time as the agent reasons through the assessment
4. Review the final report when the agent completes its analysis

## Known Issues

- Prometheus and Grafana integration is currently a work in progress and may not function as expected
- WebSocket connection may occasionally require a page refresh to establish properly

## Future Improvements

- Enhanced tool capabilities for more specialized environmental assessments
- Integration with GIS data for spatial analysis
- Improved visualization of environmental impacts
- User authentication and project management
- Additional monitoring and performance metrics


## Acknowledgments

- Built with React, FastAPI, and the ReAct framework
- Utilizes various open-source libraries and frameworks 
