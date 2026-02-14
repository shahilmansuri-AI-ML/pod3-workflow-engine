from typing import Dict, Any

class SummarizeAgent:
    def run(self, input_payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if "text" not in input_payload:
            raise ValueError("Input must contain 'text' field")
        
        text = input_payload["text"]
        
        # Simple summarization logic - extract key sentences
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Take first and last sentences, plus middle if long enough
        if len(sentences) <= 2:
            summary = '. '.join(sentences)
        elif len(sentences) <= 4:
            summary = '. '.join(sentences[:2]) + '. ' + sentences[-1]
        else:
            middle_idx = len(sentences) // 2
            summary = sentences[0] + '. ' + sentences[middle_idx] + '. ' + sentences[-1]
        
        # Calculate basic metrics
        word_count = len(text.split())
        char_count = len(text)
        summary_word_count = len(summary.split())
        
        return {
            "summary": summary.strip(),
            "original_length": {
                "characters": char_count,
                "words": word_count
            },
            "summary_length": {
                "characters": len(summary),
                "words": summary_word_count
            },
            "compression_ratio": round(summary_word_count / word_count, 2) if word_count > 0 else 0,
            "agent_metadata": {
                "agent_name": "summarize",
                "execution_context": context
            }
        }
