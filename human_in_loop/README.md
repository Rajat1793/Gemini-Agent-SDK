# Human-in-the-Loop (HITL) in Gemini Agent SDK

This demonstrates how to implement human approval/confirmation before executing sensitive operations using Gemini Agent SDK's guardrails.

## Overview

**Human-in-the-Loop** is a pattern where humans can intervene, approve, or provide input during agent execution. This is crucial for:
- Sensitive operations (delete, refund, schema changes)
- High-value transactions
- Compliance and audit requirements
- Risk mitigation

## Problem

Gemini Agent SDK doesn't have built-in human-in-the-loop like OpenAI's Guardrails. However, we can implement it using `before_tool_callback`.

## Solution

Use `before_tool_callback` to intercept tool calls and request human approval before execution.

## Implementation

### Basic Pattern

```python
from google.adk.agents import Agent
from google.adk.tools import BaseTool, ToolContext

def human_approval_callback(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext
):
    """Request approval for sensitive operations"""
    
    if tool.name in ['delete_user', 'drop_table']:
        print(f"⚠️ Approve {tool.name}?")
        response = input("yes/no: ")
        
        if response != 'yes':
            return {"result": "Operation cancelled"}
    
    return None  # Allow execution

root_agent = Agent(
    model='gemini-2.5-flash',
    name='admin_agent',
    tools=[delete_user, drop_table],
    before_tool_callback=human_approval_callback
)
```

## Features Demonstrated

### 1. **Always Require Approval**
Operations that are always sensitive:
- `delete_user_account`
- `update_database_schema`

### 2. **Threshold-Based Approval**
Conditional approval based on parameters:
- Refunds > $100
- Bulk emails > 10 recipients

### 3. **Audit Logging**
All operations logged via `after_tool_callback`:
- What was executed
- Who approved it
- When it happened

## Usage

### Run the Agent

```bash
adk run human_in_loop
```

### Test Programmatically

```bash
python human_in_loop/test_hitl.py
```

### Example Commands

Try these with the agent:

```
Delete user account 12345 for policy violation
```
→ Will ask for approval

```
Process a $150 refund for order 98765
```
→ Will ask for approval (amount > $100)

```
Process a $50 refund for order 11111
```
→ Will execute automatically (amount < $100)

```
Send email to 50 users about maintenance
```
→ Will ask for approval (recipients > 10)

```
Drop the old_logs table from database
```
→ Will ask for approval (critical operation)

## Comparison with OpenAI

OpenAI's JS SDK has **built-in HITL**: [Human-in-the-Loop Guide](https://openai.github.io/openai-agents-js/guides/human-in-the-loop/)

| Feature | OpenAI | Gemini (This Example) |
|---------|--------|----------------------|
| **Built-in HITL** | ✅ `needsApproval` flag | ❌ Manual callbacks |
| **Execution model** | ✅ PAUSES (interruptions) | ⚠️ BLOCKS (synchronous) |
| **State serialization** | ✅ JSON.stringify(state) | ❌ Not supported |
| **Resume from state** | ✅ RunState.fromString() | ❌ Not supported |
| **Before execution** | ✅ Yes | ✅ Yes (before_tool_callback) |
| **Block execution** | ✅ result.state.reject() | ✅ Return result dict |
| **Async support** | ✅ Yes | ⚠️ Sync only |
| **Batch approvals** | ✅ result.interruptions[] | ❌ One at a time |
| **Long-running approvals** | ✅ Serialize & resume later | ❌ Blocks execution |
| **Tool-level control** | ✅ Per-tool needsApproval | ✅ Native |
| **Tracing** | ✅ Automatic | ⚠️ Manual logging |

### Key Architectural Difference

**OpenAI (Non-Blocking)**:
```typescript
let result = await run(agent, 'Delete user 123');
// Execution PAUSES if approval needed
// → result.interruptions contains pending approvals
// Can serialize, shut down, resume hours later
while (result.interruptions?.length > 0) {
  // Handle approvals (can be async, web UI, etc.)
  result = await run(agent, result.state);
}
```

**Gemini (Blocking)**:
```python
# Execution BLOCKS waiting for input()
def callback(tool, args, context):
    response = input("Approve? ")  # ← Blocks here
    if response != 'yes':
        return {"result": "Cancelled"}
    return None

root_agent = Agent(
    before_tool_callback=callback  # Synchronous only
)
```

**Production Impact**:
- OpenAI: Can integrate with web/mobile UIs, approval queues, external systems
- Gemini: Limited to terminal/CLI, must respond immediately

## Architecture

```
human_in_loop/
├── agent.py              # Main HITL agent
├── test_hitl.py          # Test different scenarios
├── openai_comparison.py  # OpenAI vs Gemini comparison
└── README.md            # This file
```

## How It Works

```
User Request
     ↓
Agent Plans Action
     ↓
before_tool_callback (INTERCEPTS)
     ↓
Show Details to Human
     ↓
Request Approval (yes/no)
     ↓
   Approved?
   ├── YES → Execute Tool
   │            ↓
   │       after_tool_callback (LOG)
   │            ↓
   │       Return Result
   │
   └── NO → Return Cancellation Message
```

## Approval Rules

### Critical Operations (Always Approve)
```python
always_require_approval = [
    'delete_user_account',
    'update_database_schema'
]
```

### Threshold-Based Rules
```python
# Refunds over $100
if tool.name == 'process_refund' and args['amount'] > 100:
    needs_approval = True

# Bulk emails over 10 recipients
if tool.name == 'send_bulk_email' and args['recipient_count'] > 10:
    needs_approval = True
```

## Advanced Patterns

### 1. **Multi-Level Approval**
```python
def multi_level_approval(tool, args, context):
    if args.get('amount', 0) > 1000:
        print("Manager approval required")
        # Request manager approval
    elif args.get('amount', 0) > 100:
        print("Supervisor approval required")
        # Request supervisor approval
```

### 2. **Time-Based Approval**
```python
from datetime import datetime

def time_based_approval(tool, args, context):
    hour = datetime.now().hour
    if hour < 9 or hour > 17:
        print("⚠️ Outside business hours")
        # Always require approval
```

### 3. **Role-Based Approval**
```python
def role_based_approval(tool, args, context):
    user_role = context.get('user_role')
    
    if tool.name == 'delete_user':
        if user_role != 'admin':
            return {"result": "Insufficient permissions"}
```

### 4. **Approval Chain**
```python
def approval_chain(tool, args, context):
    approvers = ['supervisor@company.com', 'manager@company.com']
    
    for approver in approvers:
        print(f"Requesting approval from {approver}")
        # Send approval request
        # Wait for response
```

## Best Practices

### 1. **Clear Communication**
```python
print("\n" + "="*70)
print("🛑 HUMAN APPROVAL REQUIRED")
print(f"Operation: {tool.name}")
print(f"Risk Level: HIGH")
print("="*70)
```

### 2. **Audit Trail**
```python
def log_approval(tool, args, approved):
    with open('approvals.log', 'a') as f:
        f.write(f"{datetime.now()}: {tool.name} - {approved}\n")
```

### 3. **Timeout Handling**
```python
import signal

def approval_with_timeout(timeout=30):
    def timeout_handler(signum, frame):
        raise TimeoutError("Approval timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        response = input("Approve? (yes/no): ")
        signal.alarm(0)  # Cancel alarm
        return response == 'yes'
    except TimeoutError:
        return False
```

### 4. **Batch Approvals**
```python
pending_approvals = []

def batch_approval_callback(tool, args, context):
    pending_approvals.append((tool, args))
    
    if len(pending_approvals) >= 5:
        print(f"You have {len(pending_approvals)} pending approvals")
        # Show all and approve in batch
```

## Limitations

Unlike OpenAI, Gemini's HITL implementation:
- ❌ No built-in Guardrail framework
- ❌ No async approval support
- ❌ No automatic tracing integration
- ❌ Manual implementation required
- ⚠️ Synchronous input() blocks execution

## Workarounds

### 1. **Web-Based Approval UI**
Instead of `input()`, use a web interface:
```python
import flask
from threading import Event

approval_event = Event()
approval_result = None

@app.route('/approve')
def approve():
    global approval_result
    approval_result = request.args.get('approved') == 'true'
    approval_event.set()

def web_approval(tool, args):
    # Show approval UI in browser
    # Wait for approval_event
    approval_event.wait()
    return approval_result
```

### 2. **Slack/Email Approval**
```python
def slack_approval(tool, args):
    # Send Slack message with approve/deny buttons
    # Wait for callback
    # Return approval result
```

## Conclusion

Gemini Agent SDK requires manual implementation of human-in-the-loop using `before_tool_callback`, but provides fine-grained control over approval logic. For production systems, consider:

1. ✅ Use web-based approval UI
2. ✅ Implement approval queues
3. ✅ Add comprehensive logging
4. ✅ Set approval timeouts
5. ✅ Handle approval failures gracefully

OpenAI has more sophisticated built-in HITL support, but Gemini's approach offers flexibility for custom approval workflows.
