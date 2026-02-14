from app.ollama_service import generate_ai_response


class StepExecutor:

    def execute_step(self, step):

        step_type = step.get("type")

        if step_type == "ai":

            prompt = step["config"]["prompt"]

            output = generate_ai_response(prompt)

            return output

        return "Unknown step type"
