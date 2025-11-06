# Architecture Overview

## System Architecture

The Construction AI Risk Monitor follows a modern microservices architecture with the following components:

### Backend (Python/FastAPI)
- **Agents**: 14 specialized AI agents organized into:
  - Analysis agents (real-time monitoring)
  - Predictive agents (future risk prediction)
  - Strategic agents (decision support)
- **API**: RESTful API with versioning (v1)
- **Database**: PostgreSQL for persistent storage
- **Orchestrator**: Agent execution and scheduling system

### Frontend (React)
- **Dashboard**: Real-time monitoring interface
- **Components**: Modular UI components organized by function
- **State Management**: React Context API
- **Polling**: 3-second interval for real-time updates

### Infrastructure
- **Docker**: Containerized services (PostgreSQL, Redis)
- **Ollama**: Local LLM inference for recommendations

## Data Flow

```
User -> Frontend -> API (v1) -> Orchestrator -> Agents -> Database
                                                  |
                                                  v
                                              Ollama LLM
```

## Key Design Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **Modularity**: Independent, reusable components
3. **Scalability**: Async agent execution, stateless API
4. **Maintainability**: Organized directory structure, clean code
