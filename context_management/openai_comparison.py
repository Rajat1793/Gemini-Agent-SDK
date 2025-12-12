"""
OpenAI vs Gemini: Context Management Comparison

This shows how OpenAI's RunContextWrapper pattern works
and how to achieve similar functionality in Gemini.
"""

# ==================== OPENAI PATTERN ====================
"""
OpenAI provides type-safe context management via RunContextWrapper:

```python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper, Runner, function_tool

@dataclass
class UserContext:
    user_id: str
    user_name: str
    preferences: dict

@function_tool
async def get_user_age(wrapper: RunContextWrapper[UserContext]) -> str:
    # Access context via wrapper.context
    user = wrapper.context
    return f"User {user.user_name} is 47 years old"

@function_tool  
async def update_theme(
    wrapper: RunContextWrapper[UserContext],
    theme: str
) -> str:
    # Modify shared context
    wrapper.context.preferences['theme'] = theme
    return f"Theme updated to {theme} for {wrapper.context.user_name}"

async def main():
    # Create context object
    user_ctx = UserContext(
        user_id="123",
        user_name="Alice",
        preferences={'language': 'en'}
    )
    
    # Create agent with typed context
    agent = Agent[UserContext](
        name="Assistant",
        tools=[get_user_age, update_theme]
    )
    
    # Pass context to runner - available to ALL tools
    result = await Runner.run(
        starting_agent=agent,
        input="What's my age and set theme to dark",
        context=user_ctx  # ← Context injected here
    )
    
    # Context is automatically available in all tools!
    print(result.final_output)
```

Key Benefits:
✅ Type-safe (UserContext type is enforced)
✅ Automatic injection to all tools
✅ Shared mutable state across tools
✅ No global variables needed
✅ Per-run scoping (isolated contexts)
"""

# ==================== GEMINI EQUIVALENT ====================
"""
Gemini doesn't have RunContextWrapper, so we use these patterns:

### Pattern 1: Global State Dictionary

```python
from google.adk.agents import Agent

# Global context storage
USER_CONTEXT = {
    'user_id': '123',
    'user_name': 'Alice',
    'preferences': {'language': 'en'}
}

def get_user_age() -> str:
    # Access global context
    user_name = USER_CONTEXT['user_name']
    return f"User {user_name} is 47 years old"

def update_theme(theme: str) -> str:
    # Modify global context
    USER_CONTEXT['preferences']['theme'] = theme
    return f"Theme updated to {theme}"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='assistant',
    tools=[get_user_age, update_theme]
)
```

Pros: ✅ Simple, works for single-user
Cons: ❌ Not type-safe, ❌ Global state, ❌ Not isolated


### Pattern 2: Closure-Based Context

```python
def create_context_aware_tools(user_context: dict):
    '''Factory function that creates tools with captured context'''
    
    def get_user_age() -> str:
        # Access context via closure
        return f"User {user_context['user_name']} is 47 years old"
    
    def update_theme(theme: str) -> str:
        # Modify captured context
        user_context['preferences']['theme'] = theme
        return f"Theme updated to {theme}"
    
    return [get_user_age, update_theme]

# Usage
user_ctx = {
    'user_id': '123',
    'user_name': 'Alice',
    'preferences': {'language': 'en'}
}

tools = create_context_aware_tools(user_ctx)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='assistant',
    tools=tools
)
```

Pros: ✅ Better encapsulation, ✅ Per-user contexts
Cons: ❌ Still not type-safe, ❌ More complex setup


### Pattern 3: Class-Based Context Manager

```python
from typing import Dict, Optional

class UserContextManager:
    def __init__(self):
        self.contexts: Dict[str, dict] = {}
        self.active_user: Optional[str] = None
    
    def set_context(self, user_id: str, data: dict):
        self.contexts[user_id] = data
        self.active_user = user_id
    
    def get_context(self) -> Optional[dict]:
        if self.active_user:
            return self.contexts.get(self.active_user)
        return None

# Global manager instance
ctx_manager = UserContextManager()

def get_user_age() -> str:
    ctx = ctx_manager.get_context()
    if ctx:
        return f"User {ctx['user_name']} is 47 years old"
    return "No context set"

def update_theme(theme: str) -> str:
    ctx = ctx_manager.get_context()
    if ctx:
        ctx['preferences']['theme'] = theme
        return f"Theme updated to {theme}"
    return "No context set"

# Usage
ctx_manager.set_context('123', {
    'user_name': 'Alice',
    'preferences': {'language': 'en'}
})

root_agent = Agent(
    model='gemini-2.5-flash',
    name='assistant',
    tools=[get_user_age, update_theme]
)
```

Pros: ✅ Better organization, ✅ Multi-user support
Cons: ❌ Still manual, ❌ Not type-safe
"""

# ==================== COMPARISON TABLE ====================
"""
| Feature                  | OpenAI RunContextWrapper | Gemini Workarounds |
|--------------------------|--------------------------|-------------------|
| Type Safety              | ✅ Full (Generic types)  | ❌ Manual typing  |
| Automatic Injection      | ✅ Yes                   | ❌ No             |
| Per-run Isolation        | ✅ Yes                   | ⚠️ Manual         |
| Mutable Shared State     | ✅ Yes                   | ✅ Yes (global)   |
| Multi-user Support       | ✅ Easy                  | ⚠️ Requires setup |
| Clean Tool Signatures    | ✅ Yes                   | ⚠️ Cluttered      |
| Lifecycle Hook Access    | ✅ Yes                   | ❌ No             |
| Documentation/IDE Help   | ✅ Excellent             | ❌ Limited        |

VERDICT:
OpenAI's context management is significantly more sophisticated.
Gemini requires manual patterns and global state management.
"""

if __name__ == "__main__":
    print(__doc__)
