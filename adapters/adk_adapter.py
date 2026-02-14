import importlib
from typing import Dict, Any

class ADKAdapter:
    def __init__(self):
        self.agent_registry = {
            "summarize": "agents.summarize_agent.SummarizeAgent",
            "extract_entities": "agents.entity_agent.EntityAgent"
        }
    
    def invoke_agent(self, agent_name: str, input_payload: Dict[str, Any], execution_context: Dict[str, Any]) -> Dict[str, Any]:
        if agent_name not in self.agent_registry:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent_module_path = self.agent_registry[agent_name]
        module_path, class_name = agent_module_path.rsplit('.', 1)
        
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            agent = agent_class()
            
            # Prepare context for the agent
            context = {
                "execution_id": execution_context.get("execution_id"),
                "step_id": execution_context.get("step_id"),
                "step_name": execution_context.get("step_name"),
                "agent_name": agent_name
            }
            
            # Run the agent
            result = agent.run(input_payload, context)
            
            # Ensure result is serializable
            if not isinstance(result, dict):
                raise ValueError(f"Agent {agent_name} must return a dictionary")
            
            return result
            
        except ImportError as e:
            raise RuntimeError(f"Failed to import agent {agent_name}: {e}")
        except AttributeError as e:
            raise RuntimeError(f"Agent class {class_name} not found in {module_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Agent {agent_name} execution failed: {e}")
    
    def register_agent(self, agent_name: str, agent_module_path: str):
        self.agent_registry[agent_name] = agent_module_path
    
    def list_agents(self) -> Dict[str, str]:
        return self.agent_registry.copy()
