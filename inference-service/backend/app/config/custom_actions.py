"""
Custom actions for NeMo Guardrails integration.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def self_check_input(context: Optional[dict] = None) -> bool:
    """
    Custom action for input validation.
    
    This function performs custom safety checks on user input.
    Returns True if input is allowed, False otherwise.
    """
    if not context:
        return True
    
    user_message = context.get("user_message", "")
    
    # Basic safety checks
    unsafe_patterns = [
        "hack", "exploit", "malware", "virus", 
        "bypass security", "override safety", "ignore instructions",
        "jailbreak", "prompt injection"
    ]
    
    user_message_lower = user_message.lower()
    
    for pattern in unsafe_patterns:
        if pattern in user_message_lower:
            logger.warning(f"Input blocked due to unsafe pattern: {pattern}")
            return False
    
    # Additional custom checks can be added here
    
    return True


async def self_check_output(context: Optional[dict] = None) -> bool:
    """
    Custom action for output validation.
    
    This function performs custom safety checks on bot output.
    Returns True if output is allowed, False otherwise.
    """
    if not context:
        return True
    
    bot_message = context.get("bot_message", "")
    
    # Basic safety checks for output
    unsafe_output_patterns = [
        "how to hack", "exploit this", "bypass security",
        "illegal activities", "harmful instructions"
    ]
    
    bot_message_lower = bot_message.lower()
    
    for pattern in unsafe_output_patterns:
        if pattern in bot_message_lower:
            logger.warning(f"Output blocked due to unsafe pattern: {pattern}")
            return False
    
    # Additional custom checks can be added here
    
    return True


async def user_query(context: Optional[dict] = None):
    """
    Custom action for handling user queries through the RAG system.
    """
    if not context:
        return "I'm sorry, I couldn't process your request."
    
    user_message = context.get("user_message", "")
    
    try:
        # Import here to avoid circular imports
        from app.config.actions import init, get_query_response
        
        # Get the query engine and process the user message
        query_engine = init()
        response = get_query_response(query_engine, user_message)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in user_query action: {e}")
        return "I'm sorry, I encountered an error while processing your request."