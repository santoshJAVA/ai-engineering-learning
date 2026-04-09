import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# 1. Define the actual Python function (This is your "Tool")
# In production, this would make a real HTTP POST request to Jira/Linear/Trello
def create_linear_ticket(title: str, description: str, priority: str):
    """Mock function that pretends to hit an API to create a ticket."""
    print("\n" + "="*50)
    print("🚀 SYSTEM ALERT: LOCAL PYTHON FUNCTION EXECUTED BY AI!")
    print(f"   Making API Call to Linear/Jira...")
    print(f"   Title: {title}")
    print(f"   Priority: {priority.upper()}")
    print(f"   Desc: {description}")
    print("="*50 + "\n")
    
    # Return a simulated success response from the "API"
    return json.dumps({"status": "success", "ticket_id": "LIN-402", "url": "https://linear.app/ticket/LIN-402"})

# 2. Tell OpenAI what tools it has access to using JSON Schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_linear_ticket",
            "description": "Creates a new engineering task ticket in the project management system. Call this whenever the user identifies a bug or a new feature to be built.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "A concise title for the ticket.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed acceptance criteria and context.",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "The priority level of the task.",
                    },
                },
                "required": ["title", "description", "priority"],
            },
        }
    }
]

def run_pm_agent(user_message: str):
    print(f"User: '{user_message}'\n")
    print("Thinking...\n")
    
    messages = [
        {"role": "system", "content": "You are an elite Product Manager. When users describe tasks, use the ticket creation tool to organize their work."},
        {"role": "user", "content": user_message}
    ]

    # 3. Call the API, passing the tools array
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto", # Let the AI decide if it needs to use a tool
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 4. Check if the AI decided to use a tool
    if tool_calls:
        print("🤖 AI DECIDED TO USE A TOOL.")
        
        # In a real app, you loop through tool_calls in case it called multiple tools
        for tool_call in tool_calls:
            # Which function did it want to call?
            function_name = tool_call.function.name
            
            # What arguments did it decide to pass?
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🤖 AI requested to run: {function_name}")
            print(f"🤖 AI provided args: {function_args}")
            
            # 5. ACTUALLY EXECUTE THE PYTHON FUNCTION
            if function_name == "create_linear_ticket":
                function_response = create_linear_ticket(
                    title=function_args.get("title"),
                    description=function_args.get("description"),
                    priority=function_args.get("priority"),
                )
                
                # 6. Pass the result back to the LLM so it knows the tool succeeded
                messages.append(response_message) # Add the assistant's tool request to history
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                
                print("Asking AI to summarize the final result based on the tool's output...")
                # 7. Call OpenAI one last time with the tool result
                second_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                )
                print(f"\nFinal AI Response: {second_response.choices[0].message.content}")

    else:
        print(f"\nFinal AI Response: {response_message.content}")


if __name__ == "__main__":
    # Simulate a dev dropping a messy message into Slack
    slack_message = "Hey PM, the login page on mobile is overflowing the screen. Users can't click the submit button. It's happening on iOS Safari. Needs fixing ASAP before the marketing launch."
    
    run_pm_agent(slack_message)