"""
#Copilot Code
Google Gemini Agent SDK - Persistent Conversation History

This demonstrates how to save and restore conversation history across agent restarts,
similar to OpenAI's server-managed conversation_id feature.

Documentation: 
- Agent SDK: https://github.com/google-gemini/agent-developer-kit
- API Reference: https://googleapis.github.io/python-genai/
"""

from google.adk.agents import Agent
from pathlib import Path
from dotenv import load_dotenv
import logging
import json
from datetime import datetime
from typing import Dict

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('ConversationHistory')

# Conversation storage directory
CONVERSATION_DIR = Path(__file__).parent / 'conversations'
CONVERSATION_DIR.mkdir(exist_ok=True)


# ===== CONVERSATION MANAGEMENT TOOLS =====

def save_conversation_context(conversation_id: str, user_name: str, topic: str) -> str:
    """
    Save conversation context to file for persistent storage.
    
    Args:
        conversation_id: Unique identifier for this conversation
        user_name: Name of the user
        topic: Main topic of conversation
    """
    logger.info(f"💾 Saving context for conversation: {conversation_id}")
    
    file_path = CONVERSATION_DIR / f'{conversation_id}.json'
    
    # Load existing data if available
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {
            'conversation_id': conversation_id,
            'created_at': datetime.now().isoformat(),
            'contexts': []
        }
    
    # Add new context
    data['contexts'].append({
        'timestamp': datetime.now().isoformat(),
        'user_name': user_name,
        'topic': topic
    })
    data['updated_at'] = datetime.now().isoformat()
    
    # Save to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return f"✅ Context saved for conversation '{conversation_id}'\n" \
           f"   User: {user_name}\n" \
           f"   Topic: {topic}\n" \
           f"   Total contexts: {len(data['contexts'])}"


def load_conversation_context(conversation_id: str) -> str:
    """
    Load previous conversation context from file.
    
    Args:
        conversation_id: Unique identifier for the conversation to load
    """
    logger.info(f"📂 Loading context for conversation: {conversation_id}")
    
    file_path = CONVERSATION_DIR / f'{conversation_id}.json'
    
    if not file_path.exists():
        return f"❌ No conversation found with ID '{conversation_id}'\n" \
               f"   Use save_conversation_context to create a new conversation."
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    contexts = data.get('contexts', [])
    
    result = f"✅ Loaded conversation '{conversation_id}'\n"
    result += f"   Created: {data.get('created_at', 'Unknown')}\n"
    result += f"   Last Updated: {data.get('updated_at', 'Unknown')}\n"
    result += f"   Total Contexts: {len(contexts)}\n\n"
    
    if contexts:
        result += "📝 Previous Contexts:\n"
        for i, ctx in enumerate(contexts, 1):
            result += f"   {i}. {ctx.get('user_name', 'Unknown')} - {ctx.get('topic', 'No topic')}\n"
            result += f"      ({ctx.get('timestamp', 'Unknown time')})\n"
    
    return result


def list_all_conversations() -> str:
    """List all saved conversations."""
    logger.info("📋 Listing all conversations")
    
    files = list(CONVERSATION_DIR.glob('*.json'))
    
    if not files:
        return "📭 No saved conversations found."
    
    result = f"📚 Found {len(files)} conversation(s):\n\n"
    
    for file_path in sorted(files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            conv_id = data.get('conversation_id', file_path.stem)
            contexts = data.get('contexts', [])
            updated = data.get('updated_at', 'Unknown')
            
            result += f"🔹 {conv_id}\n"
            result += f"   Contexts: {len(contexts)}\n"
            result += f"   Last Updated: {updated}\n\n"
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
    
    return result


def delete_conversation(conversation_id: str) -> str:
    """
    Delete a conversation and its history.
    
    Args:
        conversation_id: ID of conversation to delete
    """
    logger.info(f"🗑️ Deleting conversation: {conversation_id}")
    
    file_path = CONVERSATION_DIR / f'{conversation_id}.json'
    
    if not file_path.exists():
        return f"❌ Conversation '{conversation_id}' not found."
    
    file_path.unlink()
    return f"✅ Deleted conversation '{conversation_id}'"


# ===== MAIN AGENT WITH PERSISTENCE =====
root_agent = Agent(
    model='gemini-2.5-flash',
    name='conversation_agent',
    description="Agent with persistent conversation storage across restarts",
    instruction="""You are a helpful assistant with persistent conversation memory.

You have access to tools that save and load conversation context to/from files:
- save_conversation_context: Save user details and topics for later recall
- load_conversation_context: Load previous conversation history
- list_all_conversations: Show all saved conversations
- delete_conversation: Remove a conversation

When users mention they want to "save" or "remember" information, use save_conversation_context.
When they ask to "load" or "recall" previous conversations, use load_conversation_context.

Example usage:
1. User: "Save this conversation as 'meeting_notes' with my name John and topic 'project planning'"
   You: Use save_conversation_context('meeting_notes', 'John', 'project planning')

2. User: "Load the conversation 'meeting_notes'"
   You: Use load_conversation_context('meeting_notes')

Be helpful and guide users on how to use persistence features.""",
    tools=[
        save_conversation_context,
        load_conversation_context,
        list_all_conversations,
        delete_conversation
    ]
)