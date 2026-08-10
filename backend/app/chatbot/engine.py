"""
BanglaMind — Main Chatbot Engine
=================================
Ties together preprocessor, intent matcher, and response generator.
"""
import logging
from backend.app.chatbot.preprocessor import BengaliPreprocessor
from backend.app.chatbot.intent_matcher import IntentMatcher
from backend.app.chatbot.response_templates import ResponseGenerator

logger = logging.getLogger(__name__)

class ChatbotEngine:
    """
    Main entry point for chatbot processing.
    """
    def __init__(self):
        self.preprocessor = BengaliPreprocessor()
        self.matcher = IntentMatcher()
        self.response_generator = ResponseGenerator()
        logger.info("ChatbotEngine initialized with rule-based models.")

    def process_message(self, message: str) -> dict:
        """
        Process an incoming message and generate a reply.
        Returns a dictionary with reply, intent details, and language.
        """
        # 1. Clean and preprocess
        clean_text = self.preprocessor.process(message)
        lang = self.preprocessor.detect_language(message)
        
        # 2. Match Intent
        match_result = self.matcher.match(clean_text)
        
        # 3. Generate Reply
        reply = self.response_generator.get_reply(match_result.tag)
        
        return {
            "reply": reply,
            "intent": {
                "tag": match_result.tag,
                "confidence": match_result.confidence,
                "score": match_result.score
            },
            "language": lang
        }

# Global singleton instance for the FastAPI app to use
engine = ChatbotEngine()
