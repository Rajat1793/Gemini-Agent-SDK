"""Test script for context management"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from context_management.agent import (
    set_user_context,
    get_user_info,
    update_preference,
    clear_user_context,
    create_user_session,
    get_session_info,
    add_session_note
)

print("\n" + "="*70)
print("Testing Context Management Patterns")
print("="*70)

# ========== TEST APPROACH 1: GLOBAL STATE ==========
print("\n" + "🔹 APPROACH 1: Global State Dictionary")
print("="*70)

print("\n1️⃣ Setting user context...")
result = set_user_context('user_123', 'Alice', 'Spanish')
print(result)

print("\n2️⃣ Getting user info...")
result = get_user_info()
print(result)

print("\n3️⃣ Updating preference (theme)...")
result = update_preference('theme', 'dark')
print(result)

print("\n4️⃣ Updating preference (timezone)...")
result = update_preference('timezone', 'UTC-5')
print(result)

print("\n5️⃣ Getting updated user info...")
result = get_user_info()
print(result)

print("\n6️⃣ Clearing context...")
result = clear_user_context()
print(result)

print("\n7️⃣ Trying to get info after clear...")
result = get_user_info()
print(result)

# ========== TEST APPROACH 2: SESSION-BASED ==========
print("\n\n" + "🔹 APPROACH 2: Session-Based Context")
print("="*70)

print("\n1️⃣ Creating user session...")
result = create_user_session('session_456', 'Bob', 'admin')
print(result)

print("\n2️⃣ Getting session info...")
result = get_session_info()
print(result)

print("\n3️⃣ Adding first note...")
result = add_session_note('User reported billing issue')
print(result)

print("\n4️⃣ Adding second note...")
result = add_session_note('Issue resolved, refund processed')
print(result)

print("\n5️⃣ Getting updated session info...")
result = get_session_info()
print(result)

# ========== DEMONSTRATE INDEPENDENCE ==========
print("\n\n" + "🔹 DEMONSTRATING PATTERN INDEPENDENCE")
print("="*70)

print("\n1️⃣ Setting new global context...")
result = set_user_context('user_789', 'Charlie', 'French')
print(result)

print("\n2️⃣ Global context info...")
result = get_user_info()
print(result)

print("\n3️⃣ Session context (still Bob)...")
result = get_session_info()
print(result)

print("\n✅ All tests completed!")
print("\n📝 Key Takeaways:")
print("   • Global state: Simple but shared across all calls")
print("   • Session-based: Better isolation and organization")
print("   • Both patterns can coexist independently")
print("="*70 + "\n")
