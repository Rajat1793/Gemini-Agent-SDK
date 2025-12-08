from google.adk.agents import Agent
from google.adk.tools import BaseTool, ToolContext
from typing import Dict, Any, Optional
import os


from google.adk.agents import Agent
from google.adk.tools import BaseTool, ToolContext
from typing import Dict, Any, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

def run_sql_query(user_query: str) -> str:
    """Simulated function to run SQL query"""
    print(f"Executing SQL query: {user_query}") 
    return f"Query executed: {user_query}"

# INPUT GUARDRAIL: Block SQL injection patterns in input
def input_guardrail(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    if tool.name == "run_sql_query":
        user_query = args.get("user_query", "")
        if not user_query or user_query.strip() == "":
            return {"result": "❌ Query cannot be empty."}
        # Block common SQL injection patterns
        sql_injection_signatures = [
            "' OR 1=1", '" OR 1=1', "--", "; DROP TABLE"
        ]
        lowered = user_query.lower()
        if any(sig.lower() in lowered for sig in sql_injection_signatures):
            return {"result": "❌ Input blocked: Detected possible SQL injection pattern."}
    return None

# OUTPUT GUARDRAIL: Block SQL injection patterns in output
def output_guardrail(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    **kwargs
) -> Optional[Dict[str, Any]]:
    # Extract result from kwargs (could be 'result' or 'tool_response')
    result = kwargs.get('result') or kwargs.get('tool_response')
    
    if tool.name == "run_sql_query" and result:
        output = result["result"] if isinstance(result, dict) and "result" in result else result
        sql_injection_signatures = [
            "' OR 1=1", '" OR 1=1', "--", "; DROP TABLE"
        ]
        lowered = str(output).lower()
        if any(sig.lower() in lowered for sig in sql_injection_signatures):
            return {"result": "❌ Output blocked: Detected possible SQL injection pattern."}
    return None

# AGENT WITH SQL INJECTION GUARDRAILS
root_agent = Agent(
    model='gemini-2.5-flash',
    name='guardrails_agent',
    description="Agent with input and output guardrails for SQL injection.",
    instruction="You help users run SQL queries, but block any input or output that looks like a SQL injection attack.",
    tools=[run_sql_query],
    before_tool_callback=input_guardrail,
    after_tool_callback=output_guardrail
)