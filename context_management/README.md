# Context Management in Gemini Agent SDK

This demonstrates context management patterns in Gemini Agent SDK, and compares with OpenAI's `RunContextWrapper` approach.

## Overview

**Problem**: Gemini Agent SDK lacks OpenAI's `RunContextWrapper` for type-safe context injection.

**Solution**: This example shows workaround patterns using:
1. Global state dictionaries
2. Session-based context managers
3. Closure-based context capture

## OpenAI's Approach (For Reference)

```python
from agents import Agent, RunContextWrapper, Runner, function_tool
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: str
    user_name: str
    preferences: dict

@function_tool
async def get_age(wrapper: RunContextWrapper[UserContext]) -> str:
    # Type-safe context access
    return f"{wrapper.context.user_name} is 47 years old"

# Context automatically injected to ALL tools
result = await Runner.run(agent, input="...", context=user_ctx)
```

**Benefits:**
- ✅ Type-safe (generic types)
- ✅ Automatic injection
- ✅ Per-run isolation
- ✅ IDE support

## Gemini Workarounds

### Pattern 1: Global State Dictionary (Simple)

```python
# Global context
USER_CONTEXT = {'user_id': None, 'user_name': None}

def set_user_context(user_id: str, user_name: str):
    USER_CONTEXT['user_id'] = user_id
    USER_CONTEXT['user_name'] = user_name

def get_user_info():
    # Access global context
    return f"User: {USER_CONTEXT['user_name']}"
```

**Pros:** Simple, works for single-user  
**Cons:** Not type-safe, global state

### Pattern 2: Session-Based Manager (Advanced)

```python
class UserSessionContext:
    def __init__(self):
        self.sessions = {}
        self.active_session = None
    
    def create_session(self, user_id, **data):
        self.sessions[user_id] = data
        self.active_session = user_id

SESSION_MANAGER = UserSessionContext()
```

**Pros:** Better organization, multi-user support  
**Cons:** Still manual management

## Usage

### Run the Agent

```bash
adk run context_management
```

### Test Programmatically

```bash
python context_management/test_context.py
```

### Example Commands

**Global State Pattern:**
```
Set context as user 123, name Alice, language Spanish
What's my user info?
Update preference theme to dark
```

**Session-Based Pattern:**
```
Create session for user 456, name Bob, role admin
Show session info
Add note: Discussed billing issue
```

## Comparison Table

| Feature | OpenAI | Gemini (This Example) |
|---------|--------|----------------------|
| **Type Safety** | ✅ Full | ❌ Manual |
| **Auto Injection** | ✅ Yes | ❌ Manual access |
| **Per-run Isolation** | ✅ Yes | ⚠️ Global state |
| **Multi-user** | ✅ Easy | ⚠️ Requires setup |
| **Clean Signatures** | ✅ Yes | ❌ Cluttered |
| **IDE Support** | ✅ Excellent | ❌ Limited |

## Files

```
context_management/
├── agent.py               # Main agent with both patterns
├── openai_comparison.py   # Detailed OpenAI comparison
├── test_context.py        # Test script
└── README.md             # This file
```

## Key Insights

1. **OpenAI Advantage**: Built-in type-safe context management
2. **Gemini Workaround**: Manual patterns using global state or closures
3. **Trade-off**: Gemini requires more boilerplate but gives you control
4. **Best Practice**: Use session-based pattern for multi-user scenarios

## When to Use Each Pattern

**Global State:**
- ✅ Single-user applications
- ✅ Simple context needs
- ✅ Rapid prototyping

**Session-Based:**
- ✅ Multi-user systems
- ✅ Complex state management
- ✅ Production applications

**OpenAI's RunContextWrapper:**
- ✅ Type safety is critical
- ✅ Complex agent systems
- ✅ Team collaboration (IDE hints)

## Limitations

Unlike OpenAI, Gemini's workarounds:
- ❌ No compile-time type checking
- ❌ Manual context passing
- ❌ No lifecycle hook integration
- ❌ Limited IDE autocomplete

## Conclusion

OpenAI's context management is **significantly more sophisticated**. Gemini requires manual implementation using standard Python patterns (global state, closures, classes).

For production systems needing robust context management, OpenAI has a clear advantage.
