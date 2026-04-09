import os
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError
from pydantic import BaseModel, Field
from typing import List, Literal
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv()
client = OpenAI()

class TicketSchema(BaseModel):
    ticket_type: Literal["bug", "feature_request", "complaint"]
    urgency: int = Field(ge=1, le=5)
    summary: str
    action_items: List[str]
    user_frustration_level: Literal["low", "medium", "high"]

# --- THIS IS THE NEW SENIOR ENGINEER PATTERN ---
# @retry automatically handles failures. 
# It waits 2^x * 1 seconds between each retry, up to 10 seconds max.
# It gives up after 4 total attempts.
# It ONLY retries on specific OpenAI network/rate-limit errors, not on your own code bugs.
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, APIStatusError)),
    reraise=True # If it fails 4 times, raise the error so your main app can handle it
)
def call_openai_with_retry(email_text: str) -> TicketSchema:
    print("Attempting to call OpenAI API...")
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract the requested data from the user email."},
            {"role": "user", "content": email_text}
        ],
        response_format=TicketSchema,
    )
    return completion.choices[0].message.parsed

def process_email(email_text: str):
    """Main wrapper function to handle the safe execution"""
    try:
        # We call the robust, retry-wrapped function
        data = call_openai_with_retry(email_text)
        return data
    except RateLimitError:
        print("❌ FATAL: We hit the rate limit and exhausted all retries. Need to pause queue.")
        return None
    except Exception as e:
        print(f"❌ FATAL: An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    sample_email = "The system is totally broken, I can't log in and I'm losing my mind. Fix it now."
    
    result = process_email(sample_email)
    
    if result:
        print("\n✅ Successfully extracted:")
        print(f"Type: {result.ticket_type} | Urgency: {result.urgency}")
        print(f"Summary: {result.summary}")