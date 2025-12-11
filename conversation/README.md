# Persistent Conversation Agent

This demonstrates how to implement persistent conversation history in Gemini Agent SDK, similar to OpenAI's server-managed `conversation_id` feature.

## Features

- **Save Conversation Context**: Store user information and topics for later recall
- **Load Previous Conversations**: Resume conversations after agent restarts
- **List All Conversations**: View all saved conversation sessions
- **Delete Conversations**: Clean up old conversation data

## How It Works

Unlike OpenAI's server-side conversation management, this implementation:

1. **Uses Tools**: Conversation persistence is implemented through callable tools
2. **File-based Storage**: Conversations stored as JSON files in `conversations/` directory
3. **Explicit Control**: Users explicitly save/load conversations via commands

## Usage

### Run the Agent

```bash
adk run conversation
```

### Example Commands

**Save a conversation:**
```
Save this conversation as 'customer_support_001' with my name Sarah and topic 'billing issue'
```

**Load a previous conversation:**
```
Load conversation 'customer_support_001'
```

**List all conversations:**
```
List all conversations
```

**Delete a conversation:**
```
Delete conversation 'customer_support_001'
```

## Comparison with OpenAI

| Feature | OpenAI | Gemini (This Implementation) |
|---------|--------|------------------------------|
| **Server-side storage** | ✅ Yes | ❌ No (file-based) |
| **Automatic history** | ✅ Yes | ⚠️ Manual (via tools) |
| **conversation_id** | ✅ Built-in | ✅ User-defined |
| **Persistence** | ✅ Automatic | ⚠️ Requires save command |
| **Cross-session** | ✅ Yes | ✅ Yes (after save) |

## Architecture

```
conversation/
├── agent.py              # Main agent with persistence tools
├── conversations/        # Stored conversation files (auto-created)
│   ├── conv_001.json
│   ├── conv_002.json
│   └── ...
└── README.md            # This file
```

## Conversation File Format

```json
{
  "conversation_id": "customer_support_001",
  "created_at": "2025-12-11T10:30:00",
  "updated_at": "2025-12-11T10:35:00",
  "contexts": [
    {
      "timestamp": "2025-12-11T10:30:00",
      "user_name": "Sarah",
      "topic": "billing issue"
    }
  ]
}
```

## Advanced Usage

### Programmatic Access

```python
from conversation.agent import (
    save_conversation_context,
    load_conversation_context,
    list_all_conversations
)

# Save context
save_conversation_context('session_123', 'John', 'Technical Support')

# Load context
context = load_conversation_context('session_123')
print(context)

# List all
conversations = list_all_conversations()
print(conversations)
```

## Limitations

1. **Manual Persistence**: Users must explicitly save conversations (not automatic like OpenAI)
2. **File-based**: Stored locally, not in cloud/database
3. **Simple Context**: Stores metadata only (name, topic), not full conversation transcript

## Future Enhancements

- [ ] Store full conversation transcript (all messages)
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] Automatic periodic saves
- [ ] Cloud storage integration
- [ ] Search across conversations
- [ ] Export conversations to different formats
