# Environmental Impact Assessment ReAct Agent

A specialized AI agent that conducts environmental impact assessments for construction projects using the ReAct (Reasoning + Acting) paradigm.

## Overview

This project implements a ReAct agent that can:

1. Analyze construction site characteristics
2. Identify applicable environmental regulations
3. Step through a structured reasoning process for environmental impact assessment
4. Use specialized tools to gather and analyze environmental data
5. Visualize the agent's reasoning and tool usage in real-time

## Project Structure

```
project/
├── backend/               # Python FastAPI backend
│   ├── app/               # Application code
│   │   ├── agent/         # ReAct agent implementation
│   │   ├── api/           # API endpoints
│   │   ├── tools/         # Specialized environmental assessment tools
│   │   └── utils/         # Utility functions
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
│
└── frontend/              # React frontend
    ├── public/            # Static assets
    └── src/               # Source code
        ├── components/    # React components
        └── services/      # API and WebSocket services
```

## Features

- **ReAct Paradigm**: Combines reasoning and tool use in an iterative process
- **Specialized Environmental Tools**:
  - Site Analysis Tool: Analyzes construction site characteristics
  - Regulatory Compliance Tool: Identifies applicable regulations
- **Real-time Reasoning Visualization**: See the agent's thought process as it happens
- **WebSocket Updates**: Get updates on the agent's state in real-time

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Gemini API key

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a .env file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. Enter an environmental assessment goal or question in the input field
2. Click "Start Assessment" to begin the agent's reasoning process
3. Watch as the agent thinks through the problem and uses specialized tools
4. View the completed assessment results when the agent finishes

## Example Tasks

- "Assess the environmental impact of a 5-story office building on a 1-acre site near a wetland"
- "Determine required environmental permits for a residential development in California"
- "Identify potential mitigation measures for a highway construction project near a protected forest"

## Technologies Used

- **Backend**: Python, FastAPI, Pydantic, WebSockets, Gemini API
- **Frontend**: React, WebSockets, CSS 