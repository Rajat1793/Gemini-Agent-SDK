"""
OpenAI vs Gemini: Human-in-the-Loop Comparison

This shows how OpenAI's approach to human-in-the-loop differs from Gemini's.

Based on: https://openai.github.io/openai-agents-js/guides/human-in-the-loop/
"""

# ==================== OPENAI APPROACH (JavaScript SDK) ====================
"""
OpenAI Agents SDK has BUILT-IN human-in-the-loop support via tool approval:

```typescript
import { tool, Agent, run } from '@openai/agents';
import z from 'zod';

// Define tool with needsApproval flag
const cancelOrder = tool({
  name: 'cancelOrder',
  description: 'Cancel order',
  parameters: z.object({
    orderId: z.number(),
  }),
  needsApproval: true,  // ← Always requires approval
  execute: async ({ orderId }) => {
    // Execute cancellation
    return `Order ${orderId} cancelled`;
  },
});

// Conditional approval based on parameters
const sendEmail = tool({
  name: 'sendEmail',
  description: 'Send an email',
  parameters: z.object({
    to: z.string(),
    subject: z.string(),
    body: z.string(),
  }),
  needsApproval: async (_context, { subject }) => {
    // Approval logic
    return subject.includes('spam');  // Require approval for spam-like subjects
  },
  execute: async ({ to, subject, body }) => {
    // Send email
  },
});

const agent = new Agent({
  name: 'Admin Agent',
  instructions: 'You can cancel orders and send emails',
  tools: [cancelOrder, sendEmail],
});

// Run agent
let result = await run(agent, 'Cancel order 123 and email customer');

// Check for interruptions (pending approvals)
while (result.interruptions?.length > 0) {
  for (const interruption of result.interruptions) {
    console.log(`Approve ${interruption.name}?`);
    console.log(`Arguments: ${interruption.arguments}`);
    
    const confirmed = await confirm('Do you approve?');
    
    if (confirmed) {
      result.state.approve(interruption);  // ← Approve
    } else {
      result.state.reject(interruption);   // ← Reject
    }
  }
  
  // Resume execution with approvals
  result = await run(agent, result.state);
}

console.log(result.finalOutput);
```

Key Features:
✅ Built-in needsApproval flag on tools
✅ Execution interrupts when approval needed
✅ result.interruptions array with pending approvals
✅ result.state.approve/reject for handling
✅ Serializable state (can pause and resume later)
✅ JSON.stringify(result.state) for persistence
✅ RunState.fromString() for deserialization
✅ Async support throughout
✅ Integrated with tracing
✅ Tool-level and conditional approval
"""

# ==================== GEMINI APPROACH ====================
"""
Gemini doesn't have built-in human-in-the-loop, but we can implement it
using before_tool_callback:

```python
from google.adk.agents import Agent
from google.adk.tools import BaseTool, ToolContext
from typing import Dict, Any, Optional

def human_approval_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    '''Request approval before executing sensitive tools'''
    
    # Check if this tool needs approval
    if tool.name == 'delete_user':
        print(f"⚠️ Approval needed for: {tool.name}")
        print(f"Arguments: {args}")
        
        response = input("Approve? (yes/no): ").strip()
        
        if response != 'yes':
            # Block execution by returning a result
            return {
                "result": "Operation cancelled by user"
            }
    
    # Allow execution
    return None

def delete_user(user_id: str) -> str:
    '''Delete a user account'''
    return f"User {user_id} deleted"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='admin_agent',
    instruction="You can delete users",
    tools=[delete_user],
    before_tool_callback=human_approval_callback  # ← Human approval
)
```

Key Differences:
⚠️ No built-in Guardrail class
⚠️ Manual implementation via callbacks
⚠️ Callback per tool, not per agent run
✅ Full control over approval logic
✅ Can inspect tool arguments
✅ Can modify or block execution
"""

# ==================== COMPARISON TABLE ====================
"""
| Feature | OpenAI | Gemini |
|---------|--------|--------|
| **Built-in HITL** | ✅ needsApproval flag | ❌ Manual via callbacks |
| **Execution interruption** | ✅ result.interruptions | ❌ Blocks in callback |
| **State serialization** | ✅ JSON.stringify(state) | ❌ Manual implementation |
| **Resume from state** | ✅ RunState.fromString() | ❌ Manual implementation |
| **Conditional approval** | ✅ async function | ✅ Callback logic |
| **Tool-level control** | ✅ Per-tool needsApproval | ✅ Per-tool callback check |
| **Async support** | ✅ Yes | ⚠️ Sync only |
| **Tracing integration** | ✅ Automatic | ⚠️ Manual logging |
| **Batch approvals** | ✅ result.interruptions array | ❌ One at a time |
| **Long-running approvals** | ✅ Serialize & resume later | ❌ Blocks execution |
| **Type safety** | ✅ Zod schemas | ⚠️ Dict-based |

KEY ARCHITECTURAL DIFFERENCES:

OpenAI:
• Execution PAUSES when approval needed → returns result.interruptions
• Non-blocking: Can serialize state and resume hours/days later
• Approvals handled OUTSIDE agent execution loop
• Multiple pending approvals processed together
• State is portable across processes/servers

Gemini:
• Execution BLOCKS when approval needed → waits for input()
• Blocking: Must respond immediately or execution hangs
• Approvals handled INSIDE before_tool_callback
• One approval at a time (synchronous)
• Cannot persist approval state

WHEN TO USE EACH:

OpenAI:
✅ Long approval times (hours/days)
✅ Need to shut down server between approval request and response
✅ Web/mobile approval UI (async workflows)
✅ Batch approval of multiple operations
✅ Production systems with approval queues
✅ Distributed approval workflows

Gemini:
✅ Immediate approval (seconds)
✅ Terminal/CLI approval workflows
✅ Simple synchronous validation
✅ Real-time interactive sessions
✅ Prototyping and testing
✅ Custom approval logic
"""

# ==================== REAL-WORLD EXAMPLE ====================
"""
SCENARIO: E-commerce admin agent that needs approval for:
1. Refunds > $100
2. Bulk email campaigns
3. Database schema changes

OpenAI Implementation (JavaScript):

```typescript
import { tool, Agent, run } from '@openai/agents';
import z from 'zod';

const processRefund = tool({
  name: 'processRefund',
  parameters: z.object({
    orderId: z.string(),
    amount: z.number(),
  }),
  needsApproval: async (_context, { amount }) => {
    return amount > 100;  // ← Conditional approval
  },
  execute: async ({ orderId, amount }) => {
    return `Refunded $${amount} for order ${orderId}`;
  },
});

const sendBulkEmail = tool({
  name: 'sendBulkEmail',
  parameters: z.object({
    recipientCount: z.number(),
    subject: z.string(),
  }),
  needsApproval: async (_context, { recipientCount }) => {
    return recipientCount > 10;
  },
  execute: async ({ recipientCount, subject }) => {
    return `Sent email to ${recipientCount} recipients`;
  },
});

const updateSchema = tool({
  name: 'updateSchema',
  needsApproval: true,  // ← Always require approval
  execute: async () => {
    return 'Schema updated';
  },
});

const agent = new Agent({
  name: 'Admin',
  tools: [processRefund, sendBulkEmail, updateSchema],
});

// Run with approval handling
let result = await run(agent, 'Process $150 refund and email 50 customers');

// Handle interruptions (can be in a different process/time)
while (result.interruptions?.length > 0) {
  // Can serialize state here and resume later
  const serialized = JSON.stringify(result.state);
  await saveToDatabase(serialized);  // Store for later
  
  // ... hours/days later ...
  
  const state = await RunState.fromString(agent, serialized);
  
  for (const interruption of result.interruptions) {
    // Show approval UI (web, mobile, Slack, etc.)
    const approved = await showApprovalUI(interruption);
    
    if (approved) {
      state.approve(interruption);
    } else {
      state.reject(interruption);
    }
  }
  
  result = await run(agent, state);  // Resume
}
```

Gemini Implementation (Python):

```python
from google.adk.agents import Agent

def approval_callback(tool, args, context):
    # Check tool name and args
    if tool.name == 'process_refund':
        amount = args.get('amount', 0)
        if amount > 100:
            print(f"⚠️ High-value refund: ${amount}")
            response = input("Approve? (yes/no): ")
            if response != 'yes':
                return {"result": "Refund cancelled"}
    
    elif tool.name == 'send_bulk_email':
        count = args.get('recipient_count', 0)
        if count > 10:
            print(f"⚠️ Bulk email: {count} recipients")
            response = input("Approve? (yes/no): ")
            if response != 'yes':
                return {"result": "Email cancelled"}
    
    elif tool.name == 'update_schema':
        print(f"⚠️ Database schema change")
        response = input("Approve? (yes/no): ")
        if response != 'yes':
            return {"result": "Schema change cancelled"}
    
    return None  # Allow execution

root_agent = Agent(
    model='gemini-2.5-flash',
    name='admin_agent',
    tools=[process_refund, send_bulk_email, update_schema],
    before_tool_callback=approval_callback
)

# LIMITATION: Must respond immediately, cannot serialize/resume
```

KEY DIFFERENCES IN PRACTICE:

OpenAI:
✅ Non-blocking: Serialize state, shut down server, resume later
✅ Multiple interruptions batched together
✅ Can integrate with external approval systems
✅ State portable across processes
✅ Perfect for web/mobile approval workflows

Gemini:
⚠️ Blocking: Must respond immediately via input()
⚠️ One approval at a time
⚠️ Tied to terminal/CLI interaction
⚠️ Cannot pause and resume execution
⚠️ Limited to synchronous workflows

PRODUCTION WORKAROUND FOR GEMINI:

To achieve OpenAI-like async approvals in Gemini:

```python
import queue
import threading

# Global approval queue
approval_queue = {}

def async_approval_callback(tool, args, context):
    if tool.name in ['process_refund', 'update_schema']:
        approval_id = f"{tool.name}_{id(args)}"
        
        # Store approval request
        approval_queue[approval_id] = {
            'tool': tool.name,
            'args': args,
            'status': 'pending'
        }
        
        # Poll for approval (with timeout)
        for _ in range(60):  # 60 second timeout
            if approval_queue[approval_id]['status'] == 'approved':
                del approval_queue[approval_id]
                return None  # Allow execution
            elif approval_queue[approval_id]['status'] == 'rejected':
                del approval_queue[approval_id]
                return {"result": "Operation cancelled"}
            
            time.sleep(1)
        
        # Timeout
        return {"result": "Approval timeout"}
    
    return None

# Separate web server handles approvals:
# POST /approve/{approval_id} → approval_queue[id]['status'] = 'approved'
# POST /reject/{approval_id} → approval_queue[id]['status'] = 'rejected'
```

This is complex and error-prone. OpenAI's built-in approach is much cleaner.
"""

if __name__ == "__main__":
    print(__doc__)
