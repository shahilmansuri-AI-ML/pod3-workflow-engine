import re
from typing import Dict, Any, List

class EntityAgent:
    def run(self, input_payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if "text" not in input_payload:
            raise ValueError("Input must contain 'text' field")
        
        text = input_payload["text"]
        
        # Simple entity extraction patterns
        entities = {
            "emails": self._extract_emails(text),
            "urls": self._extract_urls(text),
            "phone_numbers": self._extract_phone_numbers(text),
            "numbers": self._extract_numbers(text),
            "capitalized_words": self._extract_capitalized_words(text),
            "dates": self._extract_dates(text)
        }
        
        # Count total entities
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        
        return {
            "entities": entities,
            "entity_counts": {entity_type: len(entity_list) for entity_type, entity_list in entities.items()},
            "total_entities": total_entities,
            "text_stats": {
                "character_count": len(text),
                "word_count": len(text.split()),
                "sentence_count": len(text.split('.'))
            },
            "agent_metadata": {
                "agent_name": "extract_entities",
                "execution_context": context
            }
        }
    
    def _extract_emails(self, text: str) -> List[str]:
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    def _extract_urls(self, text: str) -> List[str]:
        pattern = r'https?://[^\s<>"{}|\\^`[\]]+|www\.[^\s<>"{}|\\^`[\]]+'
        return re.findall(pattern, text)
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
        return re.findall(pattern, text)
    
    def _extract_numbers(self, text: str) -> List[str]:
        pattern = r'\b\d+\.?\d*\b'
        return re.findall(pattern, text)
    
    def _extract_capitalized_words(self, text: str) -> List[str]:
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        return list(set(re.findall(pattern, text)))
    
    def _extract_dates(self, text: str) -> List[str]:
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(dates))
