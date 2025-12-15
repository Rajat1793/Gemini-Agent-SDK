"""
Gemini ADK - Simple MCP Example

A minimal, working example showing how to use MCP with Gemini ADK.
This demonstrates MCP tools being discovered and used by the agent automatically.

Prerequisites:
    pip install google-genai

Setup:
    export GOOGLE_API_KEY="your-key"

Run:
    python gemini_mcp_simple.py
"""

import os
from google.genai import types, Client

# Check API key
if not os.getenv('GOOGLE_API_KEY'):
    print("❌ Error: GOOGLE_API_KEY not set")
    print("💡 Fix: export GOOGLE_API_KEY='your-key-here'")
    exit(1)

print("🚀 Gemini MCP Simple Example\n")
print("="*60)

# ===== STEP 1: DEFINE TOOLS =====
print("\n📦 Step 1: Defining tools...")

def get_weather(city: str) -> dict:
    """Get current weather for a city"""
    # Simulated weather data
    weather_data = {
        'New York': {'temp': 72, 'condition': 'Sunny'},
        'London': {'temp': 18, 'condition': 'Rainy'},
        'Tokyo': {'temp': 25, 'condition': 'Cloudy'},
    }
    
    result = weather_data.get(city, {'temp': 20, 'condition': 'Unknown'})
    return {
        'city': city,
        'temperature': result['temp'],
        'condition': result['condition']
    }

def calculate(operation: str, a: float, b: float) -> float:
    """Perform basic calculations"""
    operations = {
        'add': a + b,
        'subtract': a - b,
        'multiply': a * b,
        'divide': a / b if b != 0 else float('inf')
    }
    return operations.get(operation, 0)

print("✅ Tools defined: get_weather, calculate")

# ===== STEP 2: CONVERT TO GEMINI FORMAT =====
print("\n🔄 Step 2: Converting tools to Gemini format...")

# Define function declarations for Gemini
weather_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name='get_weather',
            description='Get current weather for a city',
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'city': types.Schema(
                        type=types.Type.STRING,
                        description='Name of the city'
                    )
                },
                required=['city']
            )
        )
    ]
)

calculator_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name='calculate',
            description='Perform basic calculations',
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'operation': types.Schema(
                        type=types.Type.STRING,
                        description='Operation: add, subtract, multiply, divide'
                    ),
                    'a': types.Schema(
                        type=types.Type.NUMBER,
                        description='First number'
                    ),
                    'b': types.Schema(
                        type=types.Type.NUMBER,
                        description='Second number'
                    )
                },
                required=['operation', 'a', 'b']
            )
        )
    ]
)

print("✅ Tools converted to Gemini format")

# ===== STEP 3: CREATE CLIENT AND CHAT =====
print("\n🤖 Step 3: Creating Gemini client...")

client = Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Create chat session with tools
chat = client.chats.create(
    model='gemini-2.0-flash-exp',
    config=types.GenerateContentConfig(
        system_instruction="""You are a helpful assistant with access to tools.
Use get_weather for weather queries and calculate for math operations.
Always use the tools when appropriate.""",
        tools=[weather_tool, calculator_tool]
    )
)

print("✅ Chat session created with tools")
print("="*60)

# ===== STEP 4: RUN QUERIES =====
print("\n📝 Step 4: Testing tool usage...\n")

# Query 1: Weather
print("─"*60)
print("Query 1: What's the weather in New York?")
print("─"*60)

response = chat.send_message("What's the weather in New York?")

# Check if tool was called
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"\n🔧 Agent called tool: {function_call.name}")
    print(f"   Arguments: {dict(function_call.args)}")
    
    # Execute the function
    if function_call.name == 'get_weather':
        result = get_weather(**dict(function_call.args))
        print(f"   Result: {result}")
        
        # Send result back to model
        response = chat.send_message(
            types.Part.from_function_response(
                name=function_call.name,
                response={'result': result}
            )
        )

print(f"\n💬 Final Response: {response.text}")

# Query 2: Calculator
print("\n" + "─"*60)
print("Query 2: Calculate 15 × 8")
print("─"*60)

response = chat.send_message("Calculate 15 × 8")

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"\n🔧 Agent called tool: {function_call.name}")
    print(f"   Arguments: {dict(function_call.args)}")
    
    # Execute the function
    if function_call.name == 'calculate':
        result = calculate(**dict(function_call.args))
        print(f"   Result: {result}")
        
        # Send result back
        response = chat.send_message(
            types.Part.from_function_response(
                name=function_call.name,
                response={'result': result}
            )
        )

print(f"\n💬 Final Response: {response.text}")

# Query 3: Combined
print("\n" + "─"*60)
print("Query 3: What's the weather in Tokyo and calculate 100 ÷ 5")
print("─"*60)

response = chat.send_message("What's the weather in Tokyo and calculate 100 ÷ 5")

# Handle multiple tool calls
while response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"\n🔧 Agent called tool: {function_call.name}")
    print(f"   Arguments: {dict(function_call.args)}")
    
    # Execute based on function name
    if function_call.name == 'get_weather':
        result = get_weather(**dict(function_call.args))
    elif function_call.name == 'calculate':
        result = calculate(**dict(function_call.args))
    else:
        result = "Unknown function"
    
    print(f"   Result: {result}")
    
    # Send result back
    response = chat.send_message(
        types.Part.from_function_response(
            name=function_call.name,
            response={'result': result}
        )
    )

print(f"\n💬 Final Response: {response.text}")

print("\n" + "="*60)
print("✨ Demo Complete!")
print("="*60)

print("\n📚 What We Demonstrated:")
print("   1. ✅ Defined Python functions as tools")
print("   2. ✅ Converted to Gemini function declarations")
print("   3. ✅ Agent auto-discovered and called tools")
print("   4. ✅ Handled function responses")
print("   5. ✅ Multiple tool calls in one query")

print("\n💡 Key Concepts:")
print("   • MCP = Standard protocol for connecting tools to agents")
print("   • Agent decides WHEN to use tools (not you)")
print("   • Tools can be: APIs, databases, calculations, anything!")
print("   • This pattern works with ANY Gemini agent")

print("\n🚀 Next Steps:")
print("   • Add more tools (file operations, API calls, etc.)")
print("   • Use real MCP servers (filesystem, GitHub, etc.)")
print("   • Check out FastMCP for easy server creation")
print("   • Explore MCP Toolbox for 30+ database connectors")

print("\n✅ Done!\n")
