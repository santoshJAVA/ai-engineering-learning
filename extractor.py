import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal

# 1. Load environment variables (Make sure you create a .env file with OPENAI_API_KEY=sk-...)
load_dotenv()

# Initialize the OpenAI client. It automatically picks up the OPENAI_API_KEY from the environment.
client = OpenAI()

# 2. Define your strict schema using Pydantic
# This acts as both the schema we send to the LLM and the Python class we get back.
class TicketSchema(BaseModel):
    ticket_type: Literal["bug", "feature_request", "complaint"] = Field(
        description="Categorize the user's email into one of these exact three types."
    )
    urgency: int = Field(
        description="Rate the urgency from 1 (lowest) to 5 (highest) based on the user's tone.",
        ge=1, le=5
    )
    summary: str = Field(
        description="A concise, professional 1-sentence summary of the issue."
    )
    action_items: List[str] = Field(
        description="A list of specific steps or requests the user wants resolved."
    )
    user_frustration_level: Literal["low", "medium", "high"] = Field(
        description="Analyze the sentiment of the email to gauge frustration."
    )

def process_email(email_text: str) -> TicketSchema:
    """
    Takes an unstructured email string, sends it to OpenAI, 
    and forces a structured Pydantic object to be returned.
    """
    print("Sending request to OpenAI (gpt-4o-mini)...")
    
    # Notice we use .beta.chat.completions.parse instead of .create
    # This automatically handles passing the schema and parsing the JSON response.
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini", # Fast and incredibly cheap for this task
        messages=[
            {
                "role": "system", 
                "content": "You are a senior technical support parser. Extract the requested data from the user email."
            },
            {
                "role": "user", 
                "content": email_text
            }
        ],
        response_format=TicketSchema, # This is where the magic happens
    )

    # The parsed output is now a strongly typed Python object, NOT a string!
    return completion.choices[0].message.parsed


if __name__ == "__main__":
    # A messy, unstructured example email
    sample_email = """
    Hey team, 
    I've been trying to export my reports to PDF all morning and the button is just spinning. 
    This is completely unacceptable, my boss needs this presentation by noon!!! 
    Also, it would be really great if you guys could add a dark mode soon, my eyes are bleeding from staring at this bright white screen. 
    Fix the export ASAP please!
    - John
    """

    print("--- Processing Raw Email ---")
    print(sample_email.strip())
    print("\n----------------------------\n")

    try:
        # Run the extraction
        ticket_data = process_email(sample_email)

        # Because it's a Pydantic model, you get autocomplete in your IDE!
        print("\n✅ Successfully extracted strictly typed data:\n")
        print(f"Type:       {ticket_data.ticket_type.upper()}")
        print(f"Urgency:    {ticket_data.urgency}/5")
        print(f"Frustration:{ticket_data.user_frustration_level.upper()}")
        print(f"Summary:    {ticket_data.summary}")
        print("Actions:")
        for action in ticket_data.action_items:
            print(f"  - {action}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
