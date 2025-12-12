# copilot code
"""
Google Gemini Agent SDK - Context Management Example

This demonstrates how to manage context/state in Gemini Agent SDK
(workaround for OpenAI's RunContextWrapper pattern).

Since Gemini doesn't have built-in context wrappers, we use:
1. Global state dictionaries
2. Closure-based context
3. Class-based context management

Documentation: 
- Agent SDK: https://github.com/google-gemini/agent-developer-kit
- API Reference: https://googleapis.github.io/python-genai/
"""

from google.adk.agents import Agent
from pathlib import Path
from dotenv import load_dotenv
import logging
from typing import Dict, Optional
from datetime import datetime

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('ContextManagement')


# ===== APPROACH 1: GLOBAL STATE DICTIONARY =====
# Simple but works for single-user scenarios

USER_CONTEXT = {
    'user_id': None,
    'user_name': None,
    'preferences': {},
    'session_start': None
}


def set_user_context(user_id: str, user_name: str, language: str = 'en') -> str:
    """
    Set user context for the current session.
    
    Args:
        user_id: Unique user identifier
        user_name: User's display name
        language: Preferred language (default: 'en')
    """
    USER_CONTEXT['user_id'] = user_id
    USER_CONTEXT['user_name'] = user_name
    USER_CONTEXT['preferences']['language'] = language
    USER_CONTEXT['session_start'] = datetime.now().isoformat()
    
    logger.info(f"📝 Context set for user: {user_name} (ID: {user_id})")
    
    return f"✅ User context initialized:\n" \
           f"   User ID: {user_id}\n" \
           f"   Name: {user_name}\n" \
           f"   Language: {language}\n" \
           f"   Session Started: {USER_CONTEXT['session_start']}"


def get_user_info() -> str:
    """
    Get current user information from context.
    This tool has access to shared context without explicit parameters.
    """
    if not USER_CONTEXT.get('user_id'):
        return "❌ No user context set. Please use set_user_context first."
    
    logger.info(f"📖 Reading context for: {USER_CONTEXT['user_name']}")
    
    return f"👤 Current User Information:\n" \
           f"   ID: {USER_CONTEXT['user_id']}\n" \
           f"   Name: {USER_CONTEXT['user_name']}\n" \
           f"   Language: {USER_CONTEXT['preferences'].get('language', 'Unknown')}\n" \
           f"   Session Duration: {_calculate_session_duration()}"


def update_preference(key: str, value: str) -> str:
    """
    Update user preferences in context.
    
    Args:
        key: Preference key (e.g., 'theme', 'timezone')
        value: Preference value
    """
    if not USER_CONTEXT.get('user_id'):
        return "❌ No user context set. Please use set_user_context first."
    
    USER_CONTEXT['preferences'][key] = value
    logger.info(f"⚙️ Updated preference: {key} = {value}")
    
    return f"✅ Preference updated:\n" \
           f"   {key}: {value}\n" \
           f"   All Preferences: {USER_CONTEXT['preferences']}"


def clear_user_context() -> str:
    """Clear all user context data."""
    old_user = USER_CONTEXT.get('user_name', 'Unknown')
    
    USER_CONTEXT.clear()
    USER_CONTEXT.update({
        'user_id': None,
        'user_name': None,
        'preferences': {},
        'session_start': None
    })
    
    logger.info(f"🗑️ Cleared context for: {old_user}")
    return f"✅ User context cleared for {old_user}"


# ===== APPROACH 2: CLASS-BASED CONTEXT =====
# Better encapsulation and multi-user support

class UserSessionContext:
    """Encapsulated context for a user session"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.active_session: Optional[str] = None
    
    def create_session(self, user_id: str, user_name: str, **kwargs) -> str:
        """Create a new user session"""
        self.sessions[user_id] = {
            'user_id': user_id,
            'user_name': user_name,
            'created_at': datetime.now().isoformat(),
            'data': kwargs
        }
        self.active_session = user_id
        logger.info(f"🆕 Created session for: {user_name}")
        return f"Session created for {user_name}"
    
    def get_active_session(self) -> Optional[Dict]:
        """Get the currently active session"""
        if self.active_session:
            return self.sessions.get(self.active_session)
        return None
    
    def update_session_data(self, key: str, value: any) -> str:
        """Update data in active session"""
        if not self.active_session:
            return "No active session"
        
        session = self.sessions[self.active_session]
        session['data'][key] = value
        return f"Updated {key} in session"


# Global instance
SESSION_MANAGER = UserSessionContext()


def create_user_session(user_id: str, user_name: str, role: str = 'user') -> str:
    """
    Create a new user session with context.
    
    Args:
        user_id: Unique user identifier
        user_name: User's name
        role: User role (user/admin/guest)
    """
    result = SESSION_MANAGER.create_session(user_id, user_name, role=role)
    
    return f"✅ {result}\n" \
           f"   User: {user_name}\n" \
           f"   Role: {role}\n" \
           f"   Session ID: {user_id}"


def get_session_info() -> str:
    """Get information about the active session."""
    session = SESSION_MANAGER.get_active_session()
    
    if not session:
        return "❌ No active session. Create one with create_user_session."
    
    return f"📊 Active Session:\n" \
           f"   User: {session['user_name']}\n" \
           f"   ID: {session['user_id']}\n" \
           f"   Role: {session['data'].get('role', 'unknown')}\n" \
           f"   Created: {session['created_at']}\n" \
           f"   Custom Data: {session['data']}"


def add_session_note(note: str) -> str:
    """
    Add a note to the active session.
    
    Args:
        note: Note text to add
    """
    if not SESSION_MANAGER.active_session:
        return "❌ No active session"
    
    session = SESSION_MANAGER.get_active_session()
    if 'notes' not in session['data']:
        session['data']['notes'] = []
    
    session['data']['notes'].append({
        'text': note,
        'timestamp': datetime.now().isoformat()
    })
    
    return f"✅ Note added to session for {session['user_name']}\n" \
           f"   Total notes: {len(session['data']['notes'])}"


# ===== HELPER FUNCTIONS =====

def _calculate_session_duration() -> str:
    """Calculate session duration"""
    if not USER_CONTEXT.get('session_start'):
        return "Unknown"
    
    start = datetime.fromisoformat(USER_CONTEXT['session_start'])
    duration = datetime.now() - start
    
    minutes = int(duration.total_seconds() / 60)
    seconds = int(duration.total_seconds() % 60)
    
    return f"{minutes}m {seconds}s"


# ===== MAIN AGENT =====
root_agent = Agent(
    model='gemini-2.5-flash',
    name='context_management_agent',
    description="Agent demonstrating context management patterns in Gemini SDK",
    instruction="""You are a helpful assistant that demonstrates context management.

You have access to two context management approaches:

**Approach 1: Global State (Simple)**
- set_user_context: Initialize user context
- get_user_info: Retrieve current user info
- update_preference: Update user preferences
- clear_user_context: Clear context

**Approach 2: Session-Based (Advanced)**
- create_user_session: Create a new session
- get_session_info: Get active session info
- add_session_note: Add notes to session

Example flows:

1. Simple context:
   "Set my context as user ID 123, name Alice, language Spanish"
   "What's my user info?"
   "Update my preference theme to dark"

2. Session-based:
   "Create a session for user 456, name Bob, role admin"
   "Show session info"
   "Add note: Discussed billing issue"

Be helpful and guide users through both approaches!""",
    tools=[
        # Approach 1: Global State
        set_user_context,
        get_user_info,
        update_preference,
        clear_user_context,
        # Approach 2: Session-Based
        create_user_session,
        get_session_info,
        add_session_note
    ]
)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Gemini Agent SDK - Context Management Demo")
    print("="*70)
    print("\n📖 This demonstrates context management patterns in Gemini.")
    print("\n💡 Try these commands:")
    print("\n🔹 Approach 1 (Global State):")
    print("   • Set context as user 123, name Alice, language English")
    print("   • What's my user info?")
    print("   • Update preference theme to dark")
    print("   • Clear my context")
    print("\n🔹 Approach 2 (Session-Based):")
    print("   • Create session for user 456, name Bob, role admin")
    print("   • Show session info")
    print("   • Add note: First login today")
    print("\n🚀 Run with: adk run context_management")
    print("="*70 + "\n")
