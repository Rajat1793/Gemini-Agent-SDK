# Copilot code
"""
Google Gemini Agent SDK - Human-in-the-Loop Pattern

This demonstrates how to implement human approval/confirmation before executing
sensitive operations using guardrails (before_tool_callback).

Since Gemini ADK doesn't have built-in human-in-the-loop like OpenAI,
we implement it using before_tool_callback to intercept and request approval.

Documentation: 
- Agent SDK: https://github.com/google-gemini/agent-developer-kit
- API Reference: https://googleapis.github.io/python-genai/
"""

from google.adk.agents import Agent
from google.adk.tools import BaseTool, ToolContext
from pathlib import Path
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional
import sys

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('HumanInLoop')

# ===== SENSITIVE OPERATIONS =====

def delete_user_account(user_id: str, reason: str) -> str:
    """
    Delete a user account from the system.
    ⚠️ This is a sensitive operation that requires human approval.
    
    Args:
        user_id: User ID to delete
        reason: Reason for deletion
    """
    logger.info(f"🗑️ Deleting user account: {user_id}")
    
    # Simulate account deletion
    return f"✅ Account deleted successfully\n" \
           f"   User ID: {user_id}\n" \
           f"   Reason: {reason}\n" \
           f"   Status: Account permanently removed"


def process_refund(order_id: str, amount: float, reason: str) -> str:
    """
    Process a refund for an order.
    ⚠️ Requires approval for amounts over $100.
    
    Args:
        order_id: Order ID
        amount: Refund amount
        reason: Reason for refund
    """
    logger.info(f"💰 Processing refund: ${amount} for order {order_id}")
    
    # Simulate refund processing
    return f"✅ Refund processed successfully\n" \
           f"   Order ID: {order_id}\n" \
           f"   Amount: ${amount:.2f}\n" \
           f"   Reason: {reason}\n" \
           f"   Status: Funds will be returned in 3-5 business days"


def send_bulk_email(recipient_count: int, subject: str, message: str) -> str:
    """
    Send bulk email to multiple recipients.
    ⚠️ Requires approval for sending to more than 10 recipients.
    
    Args:
        recipient_count: Number of recipients
        subject: Email subject
        message: Email message
    """
    logger.info(f"📧 Sending bulk email to {recipient_count} recipients")
    
    # Simulate email sending
    return f"✅ Bulk email sent successfully\n" \
           f"   Recipients: {recipient_count}\n" \
           f"   Subject: {subject}\n" \
           f"   Status: All emails queued for delivery"


def update_database_schema(table_name: str, operation: str) -> str:
    """
    Update database schema (DROP, ALTER, etc.).
    ⚠️ This is a critical operation that always requires approval.
    
    Args:
        table_name: Name of the table
        operation: Operation to perform (DROP, ALTER, etc.)
    """
    logger.info(f"🗄️ Database schema operation: {operation} on {table_name}")
    
    # Simulate database operation
    return f"✅ Database schema updated\n" \
           f"   Table: {table_name}\n" \
           f"   Operation: {operation}\n" \
           f"   Status: Schema changes applied successfully"


# ===== HUMAN-IN-THE-LOOP GUARDRAIL =====

def human_approval_guardrail(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """
    Intercept tool calls and request human approval for sensitive operations.
    
    This guardrail checks:
    1. Always require approval for: delete_user_account, update_database_schema
    2. Require approval for refunds over $100
    3. Require approval for bulk emails to >10 recipients
    """
    
    # Define sensitive operations that always need approval
    always_require_approval = ['delete_user_account', 'update_database_schema']
    
    # Check if this tool requires approval
    needs_approval = False
    approval_reason = ""
    
    if tool.name in always_require_approval:
        needs_approval = True
        approval_reason = f"⚠️ CRITICAL OPERATION: {tool.name}"
    
    elif tool.name == 'process_refund':
        amount = args.get('amount', 0)
        if amount > 100:
            needs_approval = True
            approval_reason = f"⚠️ High-value refund: ${amount:.2f} (threshold: $100)"
    
    elif tool.name == 'send_bulk_email':
        recipient_count = args.get('recipient_count', 0)
        if recipient_count > 10:
            needs_approval = True
            approval_reason = f"⚠️ Bulk email to {recipient_count} recipients (threshold: 10)"
    
    # If approval needed, request human input
    if needs_approval:
        logger.warning(f"🚨 {approval_reason}")
        
        print("\n" + "="*70)
        print("🛑 HUMAN APPROVAL REQUIRED")
        print("="*70)
        print(f"\n{approval_reason}")
        print(f"\nTool: {tool.name}")
        print(f"Arguments:")
        for key, value in args.items():
            print(f"  • {key}: {value}")
        
        print("\n" + "-"*70)
        response = input("Do you approve this action? (yes/no): ").strip().lower()
        print("="*70 + "\n")
        
        if response != 'yes':
            logger.info("❌ Operation cancelled by human")
            return {
                "result": f"❌ Operation cancelled: {tool.name}\n" \
                         f"   Reason: User denied approval\n" \
                         f"   Status: No changes were made"
            }
        else:
            logger.info("✅ Operation approved by human")
            # Return None to allow the tool to execute
            return None
    
    # No approval needed, allow execution
    return None


# ===== OPERATION LOGGING CALLBACK =====

def log_operation_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Log all operations after execution for audit trail.
    This runs AFTER the tool executes (if approved).
    """
    result = kwargs.get('result') or kwargs.get('tool_response')
    
    logger.info(f"📝 AUDIT LOG: {tool.name} executed")
    logger.info(f"   Arguments: {args}")
    logger.info(f"   Result: {result}")
    
    # Don't modify the result, just log it
    return None


# ===== MAIN AGENT WITH HUMAN-IN-THE-LOOP =====

root_agent = Agent(
    model='gemini-2.5-flash',
    name='human_in_loop_agent',
    description="Agent with human approval for sensitive operations",
    instruction="""You are a helpful assistant that can perform various operations.

You have access to these tools:
1. delete_user_account - Delete a user account (ALWAYS requires approval)
2. process_refund - Process refunds (requires approval for amounts > $100)
3. send_bulk_email - Send bulk emails (requires approval for > 10 recipients)
4. update_database_schema - Update database schema (ALWAYS requires approval)

When performing sensitive operations, I will ask for human approval before proceeding.
Be clear about what operation you're about to perform and why.

Examples:
- "I need to delete user account 12345 due to Terms of Service violation"
- "Processing a refund of $250 for order #98765"
- "Sending email to 50 customers about system maintenance"
- "Dropping the old_logs table from the database"

Always explain the operation clearly before executing.""",
    tools=[
        delete_user_account,
        process_refund,
        send_bulk_email,
        update_database_schema
    ],
    before_tool_callback=human_approval_guardrail,
    after_tool_callback=log_operation_callback
)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Gemini Agent SDK - Human-in-the-Loop Demo")
    print("="*70)
    print("\n📖 This demonstrates human approval for sensitive operations.")
    print("\n⚠️ Operations requiring approval:")
    print("   • delete_user_account (ALWAYS)")
    print("   • update_database_schema (ALWAYS)")
    print("   • process_refund (if amount > $100)")
    print("   • send_bulk_email (if recipients > 10)")
    print("\n💡 Try these commands:")
    print("   • Delete user account 12345 for policy violation")
    print("   • Process a $150 refund for order 98765")
    print("   • Send email to 50 users about system maintenance")
    print("   • Drop the old_logs table from database")
    print("\n🚀 Run with: adk run human_in_loop")
    print("="*70 + "\n")
