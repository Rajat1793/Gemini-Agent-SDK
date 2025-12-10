"""
Google Gemini Agent SDK - Chat History Example

This demonstrates automatic conversation history in Google ADK.
The agent automatically remembers all previous messages without any manual management.

Documentation: 
- Agent SDK: https://github.com/google-gemini/agent-developer-kit
- API Reference: https://googleapis.github.io/python-genai/
"""

from google.adk.agents import Agent
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('ChatHistory')

# Create the root_agent - History is built-in and automatic!
root_agent = Agent(
    model='gemini-2.5-flash',
    name='chat_history_agent',
    description="Agent that demonstrates automatic chat history maintenance",
    instruction="""You are a helpful assistant. Reply concisely.

You automatically remember ALL previous messages in this conversation.
When users ask follow-up questions, use the conversation history to provide context-aware answers.""")