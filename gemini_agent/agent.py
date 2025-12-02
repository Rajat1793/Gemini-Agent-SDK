from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Reply to the user with a greetings message.",
    instruction="You are a helpful assistant that replies with a greetings message",
)
