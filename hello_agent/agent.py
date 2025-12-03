from google.adk.agents.llm_agent import Agent

location = 'india'

if location == 'india':
    instruction = f"Always say nameste with a greeting message and username when users location: {location}"
else:
    instruction = f"Always say hello with a greeting message and username when users location: {location}"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Reply to the user with a greetings message. based on the location",
    instruction=instruction
)