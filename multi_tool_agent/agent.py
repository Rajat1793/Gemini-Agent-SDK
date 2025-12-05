from google.adk.agents import Agent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

booking_sub_agent = Agent(
    model='gemini-2.5-flash',
    name='booking_sub_agent',
    description="Handles all flight and hotel booking operations",
    instruction="You are a booking specialist. Help users book flights and hotels with their requirements.",
)

refund_sub_agent = Agent(
    model='gemini-2.5-flash',
    name='refund_sub_agent',
    description="Handles refund requests and order cancellations",
    instruction="You are a refund specialist. Process refunds and cancellations professionally.",
)

def route_to_booking(destination: str, date: str, passengers: int) -> str:
    """Book a flight for the customer."""
    return f"✓ Successfully booked ticket to {destination} for {passengers} passenger(s) on {date}. Confirmation number: BK-12345"

def route_to_refund(order_id: str, reason: str) -> str:
    """Process a refund for the customer."""
    return f"✓ Refund processed successfully. Order ID: {order_id}. Reason: {reason}. Refund amount: $500. Processing time: 3-5 business days."

root_agent = Agent(
    model='gemini-2.5-flash',
    name='customer_service_agent',
    description="Main customer service agent that books flights and processes refunds",
    instruction="""You are a customer service agent. When user asks for:
1. Bookings: Use route_to_booking tool with destination, date, and number of passengers
2. Refunds: Use route_to_refund tool with order_id and reason

Always call the appropriate tool and provide the complete response to the user.""",
    tools=[route_to_booking, route_to_refund]
)

