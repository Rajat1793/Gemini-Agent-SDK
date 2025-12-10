"""
Google Gemini Agent SDK - Chat History Example

This example demonstrates how the agent automatically maintains conversation history
across multiple turns without requiring manual history management.

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

# Optional tool to demonstrate history with tool calls
def remember_info(name: str, detail: str) -> str:
    """Store information about the user for later recall."""
    logger.info(f"📝 Storing: {name} = {detail}")
    return f"✓ Remembered: {name} is {detail}"

def recall_info(topic: str) -> str:
    """Recall information from conversation history."""
    logger.info(f"🔍 Attempting to recall: {topic}")
    return f"Checking conversation history for information about: {topic}"

# Create the root_agent with chat history support
root_agent = Agent(
    model='gemini-2.5-flash',
    name='chat_history_agent',
    description="Agent that demonstrates automatic chat history maintenance",
    instruction="""You are a helpful assistant that demonstrates chat history capabilities.

Key behaviors:
1. You automatically remember ALL previous messages in the current conversation
2. When users ask about previous information, recall it from the chat history
3. You can reference earlier parts of the conversation naturally
4. You have access to tools to explicitly remember and recall information

Available tools:
- remember_info: Store specific information (name, detail)
- recall_info: Search conversation history for a topic

Be friendly, conversational, and demonstrate your memory by referencing earlier messages!""",
    tools=[remember_info, recall_info]
)

