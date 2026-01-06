"""
LLM Module: Handles Gemini (primary) and Ollama (fallback) integration.
Ensures conversation state persists across fallback.
"""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
except ImportError:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain.schema import HumanMessage, AIMessage, BaseMessage
    except ImportError:
        # Fallback if langchain not available
        ChatGoogleGenerativeAI = None
        BaseMessage = object
        HumanMessage = object
        AIMessage = object
import ollama
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class LLMProvider:
    """Manages LLM interactions with automatic fallback."""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.conversation_history: List = []
        self.use_gemini = True
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API if key is available."""
        if ChatGoogleGenerativeAI is None:
            logger.warning("LangChain Google GenAI not available, using Ollama fallback")
            self.use_gemini = False
            return
            
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model=self.gemini_model,
                    google_api_key=self.gemini_api_key,
                    temperature=0.7
                )
                logger.info(f"Gemini API initialized with model: {self.gemini_model}")
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                self.use_gemini = False
        else:
            logger.warning("Gemini API key not found, using Ollama fallback")
            self.use_gemini = False
    
    def _convert_to_ollama_messages(self, messages: List) -> List[Dict]:
        """Convert LangChain messages to Ollama format."""
        ollama_messages = []
        for msg in messages:
            # Handle both LangChain message objects and dict-like objects
            if hasattr(msg, 'content'):
                if isinstance(msg, HumanMessage) or (hasattr(msg, '__class__') and 'Human' in str(msg.__class__)):
                    ollama_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage) or (hasattr(msg, '__class__') and 'AI' in str(msg.__class__)):
                    ollama_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, dict):
                # Already in dict format
                ollama_messages.append(msg)
        return ollama_messages
    
    def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Gemini API."""
        try:
            messages = self.conversation_history.copy()
            if system_prompt:
                # Add system prompt as first message
                if HumanMessage != object:
                    messages.insert(0, HumanMessage(content=system_prompt))
                else:
                    messages.insert(0, {"role": "user", "content": system_prompt})
            if HumanMessage != object:
                messages.append(HumanMessage(content=prompt))
            else:
                messages.append({"role": "user", "content": prompt})
            
            response = self.gemini_llm.invoke(messages)
            response_text = response.content
            
            # Update conversation history
            if HumanMessage != object:
                self.conversation_history.append(HumanMessage(content=prompt))
                self.conversation_history.append(AIMessage(content=response_text))
            else:
                # Fallback to dict format
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama API as fallback."""
        try:
            messages = self._convert_to_ollama_messages(self.conversation_history)
            
            if system_prompt:
                # Ollama doesn't have explicit system messages, prepend to first user message
                if messages and messages[0]["role"] == "user":
                    messages[0]["content"] = f"{system_prompt}\n\n{messages[0]['content']}"
                else:
                    messages.insert(0, {"role": "user", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(
                model=self.ollama_model,
                messages=messages,
                options={"temperature": 0.7}
            )
            
            response_text = response["message"]["content"]
            
            # Update conversation history
            if HumanMessage != object:
                self.conversation_history.append(HumanMessage(content=prompt))
                self.conversation_history.append(AIMessage(content=response_text))
            else:
                # Fallback to dict format
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response with automatic fallback.
        Maintains conversation state across fallback.
        """
        if self.use_gemini:
            try:
                return self._call_gemini(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"Falling back to Ollama: {e}")
                self.use_gemini = False
                return self._call_ollama(prompt, system_prompt)
        else:
            return self._call_ollama(prompt, system_prompt)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List:
        """Get current conversation history."""
        return self.conversation_history.copy()

