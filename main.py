from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# We import the robust function you just built!
# (Ensure your previous script is named robust_extractor.py and is in the same folder)
from robust_extractor import process_email, TicketSchema

# Initialize the FastAPI app
app = FastAPI(
    title="AI Support Triage API",
    description="An API that turns messy customer emails into structured JSON tickets."
)

# Define the expected input schema for the API
class EmailRequest(BaseModel):
    email_text: str

# Define the POST endpoint
# Notice how we use the TicketSchema from your AI script as the response_model!
@app.post("/api/extract-ticket", response_model=TicketSchema)
async def extract_ticket_endpoint(request: EmailRequest):
    print(f"Received API request with email length: {len(request.email_text)}")
    
    # Run your robust, retry-wrapped AI logic
    result = process_email(request.email_text)
    
    if not result:
        # If the rate limit failed 4 times, return a proper 503 HTTP error
        raise HTTPException(
            status_code=503, 
            detail="AI Provider is currently unavailable. Please try again later."
        )
        
    return result

# Note: You don't need an if __name__ == "__main__" block here.
# You will run this using the uvicorn server (see instructions below).