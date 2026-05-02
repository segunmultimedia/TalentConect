import os
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="J Mime Ministry API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactRequest(BaseModel):
    name: str
    email: str
    event_details: str
    message: str


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
DESTINATION_EMAIL = os.getenv("DESTINATION_EMAIL")

print(f"DEBUG: Using username={SMTP_USERNAME}")


@app.post("/api/contact")
async def handle_contact_form(request: ContactRequest):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise HTTPException(status_code=500, detail="SMTP credentials not configured.")

    try:
        msg = EmailMessage()
        msg.set_content(
            f"""
New Ministration Request:

Name/Organization: {request.name}
Email: {request.email}
Event Details: {request.event_details}

Message:
{request.message}
"""
        )
        msg["Subject"] = f"New Booking Request from {request.name}"
        msg["From"] = SMTP_USERNAME
        msg["To"] = DESTINATION_EMAIL

        # Use SMTP_SSL for port 465
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email.")
