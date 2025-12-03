from google.adk.agents import Agent
import os, requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

def send_weather_email(recipient_email, city):
    try:
        weather_info = get_weather(city)
        subject = f"Weather Report for {city}"
        body = f"Hello,\n\n{weather_info}\n\nBest regards,\nWeather Assistant"
        result = send_email(recipient_email, subject, body)
        return result
    except Exception as e:
        return f"Error: {str(e)}"
    
def send_email(recipient_email, subject, body):
    try:
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            return "Error in configuration"
        
        #create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        #send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        
        return f"Email sent successfully to {recipient_email}"
    except smtplib.SMTPAuthenticationError:
        return "Error: Invalid email or app password. Check your .env configuration."
    except Exception as e:
        return f"Error sending email: {str(e)}"


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Reply to the user with a greetings message. Provide weather information when requested and send it via email if asked.",
    instruction="You are a helpful assistant that greets the user with a greeting message, provides weather information when requested, and can send weather reports via email.",
    tools = [get_weather, send_email, send_weather_email]
)