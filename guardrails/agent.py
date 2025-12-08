from google.adk.agents import Agent
from google.adk.tools import BaseTool, ToolContext
from typing import Dict, Any, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

def solve_math(math_problem: str) -> str:
    """Solve simple math problems."""
    try:
        result = eval(math_problem)
        return f"✓ Result: {result}"
    except Exception as e:
        return f"❌ Error solving: {str(e)}"

def validate_tool_inputs(
    tool: BaseTool, 
    args: Dict[str, Any], 
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """
    Guardrail: Validate tool arguments before execution.
    Returns None to allow execution, or a dict to block and return that instead.
    """
    
    # Only validate the solve_math tool
    if tool.name == "solve_math":
        math_problem = args.get("math_problem", "")
        
        # Guardrail 1: Block empty input
        if not math_problem or math_problem.strip() == "":
            return {"result": "❌ Empty math problem not allowed"}
        
        # Guardrail 2: Length limit
        if len(math_problem) > 50:
            return {"result": "❌ Math problem too long. Keep it under 50 characters"}
        
        # Guardrail 3: Block dangerous operations
        banned_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
        if any(keyword in math_problem.lower() for keyword in banned_keywords):
            return {"result": "❌ Potentially unsafe operation blocked"}
        
        print(f"✓ Guardrail passed for: {math_problem}")
    
    # Return None to allow the tool to execute
    return None

root_agent = Agent(
    model='gemini-2.5-flash',
    name='guardrails_agent',
    description="Math agent with input validation guardrails",
    instruction="You help users solve simple math problems. Use the solve_math tool for calculations.",
    tools=[solve_math],
    before_tool_callback=validate_tool_inputs 
)