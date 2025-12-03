from google.adk.agents import Agent
import os, requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

def get_weather(city):
    print(f"Fetching weather for {city}...")
    url = f'https://wttr.in/{city.lower()}?format=%C+%t'
    try:
        # Timeout set to 10 seconds - waits for API response
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return f'The current weather in {city} is: {response.text}'
        else:
            return f'Failed to fetch weather: Status code {response.status_code}'
    except Exception as e:
        return f'Unable to fetch weather for {city}: {str(e)}'
    
# TODO: Create a tool to send the weather information to the user email

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Reply to the user with a greetings message. and let them know weather information when requested.",
    instruction="You are a helpful assistant that greet the user with a gretting message and  provides weather information when requested.",
    tools = [get_weather, get_time]
)