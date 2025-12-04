from google.adk.agents import Agent
import os, requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional

# Load .env from root directory
root_env = Path(__file__).parent.parent / '.env'
load_dotenv(root_env)

# Structured output models
class WeatherResponse(BaseModel):
    """Structured weather response"""
    city: str
    degree: float
    condition: str
    status: str = Field(description="success or error")
    error_message: Optional[str] = None

def get_weather(city: str) -> dict:
    """Get weather with structured output"""
    print(f"Fetching weather for {city}...")
    url = f'https://wttr.in/{city.lower()}?format=%C+%t'
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            result = WeatherResponse(
                city=city,
                degree=float(response.text.split()[1].replace('°C','')),
                condition=response.text.split()[0],
                status="success"
            )
            return result.model_dump()
        else:
            result = WeatherResponse(
                city=city,
                degree=0.0,
                condition="",
                status="error",
                error_message=f"Status code {response.status_code}"
            )
            return result.model_dump()
    except Exception as e:
        result = WeatherResponse(
            city=city,
            degree=0.0,
            condition="",
            status="error",
            error_message=str(e)
        )
        return result.model_dump()

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
    tools = [get_weather, send_email, send_weather_email],
    output_schema=WeatherResponse
)