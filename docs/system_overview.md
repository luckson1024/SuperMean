# SuperMean Architectural Overview

## Core Components
```mermaid
graph TD
  A[SuperAgent] --> B[Planner]
  A --> C[Evaluator]
  A --> D[Tool Creator]
  B --> E[Medical Agent]
  B --> F[Research Agent]
  C --> G[Skill Library]
  D --> H[Model Router]
```

## Implementation Progress
| Module | Completion | Tests Passing |
|--------|------------|----------------|
| MedicalAgent | 90% | ✓✓✓✗ |
| ModelRouter | 75% | ✓✓✗✗ |
| Planner | 60% | ✓✗✗✗ |

## Dependency Map
```
model_router.py
  ├── gemini_connector.py
  ├── deepseek_connector.py
  └── routerapi_connector.py

medical_agent.py
  ├── base_agent.py
  └── model_router.py
```

## Active Integration Points
1. Model Router → Gemini API
2. Medical Agent → Web Search Skill
3. Planner → Agent Memory System