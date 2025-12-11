"""Test script for conversation persistence"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation.agent import (
    save_conversation_context,
    load_conversation_context,
    list_all_conversations,
    delete_conversation
)

print("\n" + "="*70)
print("Testing Conversation Persistence")
print("="*70)

# Test 1: Save a conversation
print("\n1️⃣ Saving conversation 'demo_123'...")
result = save_conversation_context('demo_123', 'Alice', 'AI development')
print(result)

# Test 2: Save another context to same conversation
print("\n2️⃣ Adding more context to 'demo_123'...")
result = save_conversation_context('demo_123', 'Alice', 'Python coding')
print(result)

# Test 3: List all conversations
print("\n3️⃣ Listing all conversations...")
result = list_all_conversations()
print(result)

# Test 4: Load the conversation
print("\n4️⃣ Loading conversation 'demo_123'...")
result = load_conversation_context('demo_123')
print(result)

# Test 5: Create another conversation
print("\n5️⃣ Saving conversation 'support_456'...")
result = save_conversation_context('support_456', 'Bob', 'Technical support')
print(result)

# Test 6: List all again
print("\n6️⃣ Listing all conversations again...")
result = list_all_conversations()
print(result)

# Test 7: Delete a conversation
print("\n7️⃣ Deleting conversation 'support_456'...")
result = delete_conversation('support_456')
print(result)

# Test 8: List final state
print("\n8️⃣ Final conversation list...")
result = list_all_conversations()
print(result)

print("\n✅ All tests completed!")
print("="*70 + "\n")
