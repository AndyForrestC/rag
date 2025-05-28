"""
NeMo Guardrails integration service for content safety and moderation.
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from nemoguardrails import LLMRails, RailsConfig
except ImportError as e:
    logging.warning(f"NeMo Guardrails not available: {e}")
    LLMRails = None
    RailsConfig = None

logger = logging.getLogger(__name__)


class GuardrailsService:
    """Service for managing NeMo Guardrails integration."""
    
    def __init__(self):
        self.rails: Optional[LLMRails] = None
        self._initialize_rails()
    
    def _initialize_rails(self):
        """Initialize the NeMo Guardrails system."""
        if LLMRails is None or RailsConfig is None:
            logger.warning("NeMo Guardrails not available. Guardrails will be disabled.")
            return
        
        try:
            # Get the config directory path
            config_dir = Path(__file__).parent.parent / "config"
            
            # Check if config files exist
            config_file = config_dir / "config.yml"
            flows_file = config_dir / "bot_flows.co"
            
            if not config_file.exists():
                logger.warning(f"Guardrails config file not found: {config_file}")
                return
            
            if not flows_file.exists():
                logger.warning(f"Guardrails flows file not found: {flows_file}")
                return
            
            # Initialize the guardrails configuration
            config = RailsConfig.from_path(str(config_dir))
            
            # Create the LLMRails instance
            self.rails = LLMRails(config)
            
            logger.info("NeMo Guardrails initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NeMo Guardrails: {e}")
            self.rails = None
    
    def is_enabled(self) -> bool:
        """Check if guardrails are enabled and working."""
        return self.rails is not None
    
    async def check_input(self, user_input: str) -> Dict[str, Any]:
        """
        Check user input against safety rails.
        
        Args:
            user_input: The user's input message
            
        Returns:
            Dict containing:
            - allowed: bool - whether input is allowed
            - reason: str - reason if blocked
            - modified_input: str - potentially modified input
        """
        if not self.is_enabled():
            # If guardrails are disabled, allow all input
            return {
                "allowed": True,
                "reason": "Guardrails disabled",
                "modified_input": user_input
            }
        
        try:
            # Use NeMo Guardrails to check the input
            # This will run through the self_check_input flow
            response = await self.rails.generate_async(
                messages=[{"role": "user", "content": user_input}]
            )
            
            # Check if the response was blocked
            if hasattr(response, 'last_bot_message') and response.last_bot_message:
                bot_message = response.last_bot_message.get('content', '')
                if "I'm sorry, I can't respond to that." in bot_message:
                    return {
                        "allowed": False,
                        "reason": "Input blocked by safety rails",
                        "modified_input": user_input
                    }
            
            return {
                "allowed": True,
                "reason": "Input passed safety checks",
                "modified_input": user_input
            }
            
        except Exception as e:
            logger.error(f"Error checking input with guardrails: {e}")
            # In case of error, allow the input but log the issue
            return {
                "allowed": True,
                "reason": f"Guardrails check failed: {e}",
                "modified_input": user_input
            }
    
    async def check_output(self, bot_output: str, user_input: str = "") -> Dict[str, Any]:
        """
        Check bot output against safety rails.
        
        Args:
            bot_output: The bot's generated response
            user_input: The original user input (for context)
            
        Returns:
            Dict containing:
            - allowed: bool - whether output is allowed
            - reason: str - reason if blocked
            - modified_output: str - potentially modified output
        """
        if not self.is_enabled():
            # If guardrails are disabled, allow all output
            return {
                "allowed": True,
                "reason": "Guardrails disabled",
                "modified_output": bot_output
            }
        
        try:
            # Create a conversation context for output checking
            messages = []
            if user_input:
                messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": bot_output})
            
            # Use NeMo Guardrails to check the output
            response = await self.rails.generate_async(messages=messages)
            
            # Check if the output was modified or blocked
            if hasattr(response, 'last_bot_message') and response.last_bot_message:
                checked_content = response.last_bot_message.get('content', bot_output)
                
                if "I'm sorry, I can't respond to that." in checked_content:
                    return {
                        "allowed": False,
                        "reason": "Output blocked by safety rails",
                        "modified_output": "I apologize, but I cannot provide that response due to safety guidelines."
                    }
                
                return {
                    "allowed": True,
                    "reason": "Output passed safety checks",
                    "modified_output": checked_content
                }
            
            return {
                "allowed": True,
                "reason": "Output passed safety checks",
                "modified_output": bot_output
            }
            
        except Exception as e:
            logger.error(f"Error checking output with guardrails: {e}")
            # In case of error, allow the output but log the issue
            return {
                "allowed": True,
                "reason": f"Guardrails check failed: {e}",
                "modified_output": bot_output
            }
    
    async def generate_safe_response(self, user_input: str) -> Dict[str, Any]:
        """
        Generate a response using the full guardrails pipeline.
        
        Args:
            user_input: The user's input message
            
        Returns:
            Dict containing the safe response and metadata
        """
        if not self.is_enabled():
            return {
                "response": None,
                "handled_by_guardrails": False,
                "reason": "Guardrails disabled"
            }
        
        try:
            # Generate response through guardrails
            response = await self.rails.generate_async(
                messages=[{"role": "user", "content": user_input}]
            )
            
            if hasattr(response, 'last_bot_message') and response.last_bot_message:
                bot_response = response.last_bot_message.get('content', '')
                
                return {
                    "response": bot_response,
                    "handled_by_guardrails": True,
                    "reason": "Response generated through guardrails"
                }
            
            return {
                "response": None,
                "handled_by_guardrails": False,
                "reason": "No response generated by guardrails"
            }
            
        except Exception as e:
            logger.error(f"Error generating response with guardrails: {e}")
            return {
                "response": None,
                "handled_by_guardrails": False,
                "reason": f"Guardrails generation failed: {e}"
            }


# Global instance
_guardrails_service = None

def get_guardrails_service() -> GuardrailsService:
    """Get the global guardrails service instance."""
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service