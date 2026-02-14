from typing import Dict, Any
from adapters.ollama_adapter import generate

class OllamaAgent:

    def run(self, input_payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:

        if "text" not in input_payload:
            raise ValueError("Input must contain 'text'")

        prompt = input_payload["text"]

        response = generate(prompt)

        return {
            "response": response,
            "agent_metadata": {
                "agent_name": "ollama",
                "execution_context": context
            }
        }
