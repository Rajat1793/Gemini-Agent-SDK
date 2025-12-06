from google.adk.agents import Agent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# ===== SPECIALIZED SUB-AGENTS =====
booking_agent = Agent(
    model='gemini-2.5-flash',
    name='booking_agent',
    description="Specialist agent for flight and hotel bookings",
    instruction="""You are a booking specialist. When you receive a booking request:
1. Confirm the destination, date, and number of passengers
2. Provide booking confirmation with a confirmation number
3. Offer additional services if relevant (hotels, car rentals)""",
)

refund_agent = Agent(
    model='gemini-2.5-flash',
    name='refund_agent',
    description="Specialist agent for refunds and cancellations",
    instruction="""You are a refund specialist. When you receive a refund request:
1. Confirm the order ID and reason for refund
2. Provide refund confirmation and processing time
3. Be empathetic and professional""",
)

# ===== HANDOFF TOOLS =====
def handoff_to_booking_agent(user_request: str) -> str:
    """Handoff customer to booking specialist agent. Use when customer wants to book flights or hotels."""
    return f"[HANDOFF] Transferring to booking specialist for: {user_request}"

def handoff_to_refund_agent(user_request: str) -> str:
    """Handoff customer to refund specialist agent. Use when customer wants refunds or cancellations."""
    return f"[HANDOFF] Transferring to refund specialist for: {user_request}"

# ===== MAIN ROUTER AGENT (with handoff pattern) =====
root_agent = Agent(
    model='gemini-2.5-flash',
    name='customer_service_router',
    description="Main customer service router that hands off to specialist agents",
    instruction="""You are the first point of contact for customer service. Your job is to understand customer needs and handoff to the right specialist:

1. For bookings (flights, hotels) → use handoff_to_booking_agent
2. For refunds/cancellations → use handoff_to_refund_agent

After handoff, the specialist agent will take over the conversation.""",
    tools=[handoff_to_booking_agent, handoff_to_refund_agent, booking_agent, refund_agent]
)

