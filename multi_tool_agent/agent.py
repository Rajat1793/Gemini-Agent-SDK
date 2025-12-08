from google.adk.agents import Agent
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# ===== SETUP LOGGING FOR TRACING =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('AgentFlow')

# ===== BOOKING TOOL =====
def book_flight(destination: str, date: str, passengers: int) -> str:
    """Book a flight for customers."""
    logger.info(f"🛫 Booking flight to {destination} for {passengers} passenger(s) on {date}")
    return f"✓ Flight booked successfully!\n" \
           f"   Destination: {destination}\n" \
           f"   Date: {date}\n" \
           f"   Passengers: {passengers}\n" \
           f"   Confirmation: BK-{hash(destination) % 100000:05d}"

# ===== REFUND TOOL =====
def process_refund(order_id: str, reason: str) -> str:
    """Process refund for customers."""
    logger.info(f"💰 Processing refund for order {order_id}")
    return f"✓ Refund processed successfully!\n" \
           f"   Order ID: {order_id}\n" \
           f"   Reason: {reason}\n" \
           f"   Refund Amount: $500\n" \
           f"   Processing Time: 3-5 business days"

# ===== CHECK STATUS TOOL =====
def check_booking_status(confirmation_number: str) -> str:
    """Check booking status."""
    logger.info(f"📋 Checking status for {confirmation_number}")
    return f"✓ Booking Status: Confirmed\n" \
           f"   Confirmation: {confirmation_number}\n" \
           f"   Status: Active\n" \
           f"   Check-in: Available 24 hours before departure"

# ===== MAIN AGENT =====
root_agent = Agent(
    model='gemini-2.5-flash',
    name='customer_service_agent',
    description="Customer service agent that handles bookings, refunds, and status checks",
    instruction="""You are a helpful customer service agent with access to three tools:

1. book_flight - Book flights for customers (destination, date, passengers)
2. process_refund - Process refunds (order_id, reason)
3. check_booking_status - Check booking status (confirmation_number)

Analyze customer requests and use the appropriate tool. Be friendly and professional.""",
    tools=[book_flight, process_refund, check_booking_status]
)