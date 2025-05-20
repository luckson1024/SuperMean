# ModelContextProtocol (MCP): Standardizes agent/tool/skill context
from typing import Dict, Any

class ModelContextProtocol:
    def __init__(self, name: str, context: Dict[str, Any], capabilities: Dict[str, Any], requirements: Dict[str, Any]):
        self.name = name
        self.context = context
        self.capabilities = capabilities
        self.requirements = requirements

    def describe(self):
        return {
            'name': self.name,
            'context': self.context,
            'capabilities': self.capabilities,
            'requirements': self.requirements
        }
