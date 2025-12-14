"""
Test script for Human-in-the-Loop pattern

This demonstrates different approval scenarios:
1. Operations that always require approval
2. Conditional approval based on thresholds
3. Automatic approval for safe operations
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from human_in_loop.agent import (
    delete_user_account,
    process_refund,
    send_bulk_email,
    update_database_schema,
    human_approval_guardrail
)
from google.adk.tools import BaseTool, ToolContext
from unittest.mock import Mock

print("\n" + "="*70)
print("Testing Human-in-the-Loop Guardrails")
print("="*70)

# Create mock tool and context for testing
def test_guardrail(tool_name: str, args: dict):
    """Helper function to test the guardrail"""
    mock_tool = Mock(spec=BaseTool)
    mock_tool.name = tool_name
    mock_context = Mock(spec=ToolContext)
    
    result = human_approval_guardrail(mock_tool, args, mock_context)
    
    if result is None:
        print(f"✅ Operation approved (or no approval needed)")
    else:
        print(f"⚠️ Guardrail triggered: {result}")

# ========== TEST 1: CRITICAL OPERATIONS ==========
print("\n" + "🔹 TEST 1: Critical Operations (Always Require Approval)")
print("="*70)

print("\n1️⃣ Testing delete_user_account...")
print("   This should ALWAYS trigger approval request")
test_guardrail('delete_user_account', {
    'user_id': '12345',
    'reason': 'ToS violation'
})

print("\n2️⃣ Testing update_database_schema...")
print("   This should ALWAYS trigger approval request")
test_guardrail('update_database_schema', {
    'table_name': 'users',
    'operation': 'DROP'
})

# ========== TEST 2: THRESHOLD-BASED APPROVAL ==========
print("\n\n" + "🔹 TEST 2: Threshold-Based Approval")
print("="*70)

print("\n1️⃣ Testing small refund ($50) - Should NOT need approval...")
test_guardrail('process_refund', {
    'order_id': 'ORD-001',
    'amount': 50.0,
    'reason': 'Wrong item'
})

print("\n2️⃣ Testing large refund ($250) - Should need approval...")
test_guardrail('process_refund', {
    'order_id': 'ORD-002',
    'amount': 250.0,
    'reason': 'Defective product'
})

# ========== TEST 3: BULK OPERATIONS ==========
print("\n\n" + "🔹 TEST 3: Bulk Operations")
print("="*70)

print("\n1️⃣ Testing small email batch (5 recipients) - Should NOT need approval...")
test_guardrail('send_bulk_email', {
    'recipient_count': 5,
    'subject': 'Weekly newsletter',
    'message': 'Check out our new features!'
})

print("\n2️⃣ Testing large email batch (100 recipients) - Should need approval...")
test_guardrail('send_bulk_email', {
    'recipient_count': 100,
    'subject': 'System maintenance',
    'message': 'Scheduled downtime this weekend'
})

# ========== SUMMARY ==========
print("\n\n" + "="*70)
print("Test Summary")
print("="*70)
print("""
✅ Human-in-the-Loop Guardrail Features:

1. CRITICAL OPERATIONS (Always require approval):
   • delete_user_account
   • update_database_schema

2. THRESHOLD-BASED APPROVAL:
   • Refunds > $100
   • Bulk emails > 10 recipients

3. AUDIT LOGGING:
   • All operations logged via after_tool_callback
   • Complete audit trail maintained

4. USER EXPERIENCE:
   • Clear approval prompts
   • Shows operation details before execution
   • Allows cancellation at any time
""")
print("="*70 + "\n")
