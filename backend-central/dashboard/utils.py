# dashboard/utils.py

from dotenv import load_dotenv
import os
from nylas import Client
import requests
from sqlalchemy.orm import Session
from db.models import Wallet  # assuming Wallet class is in models.py

# Load environment variables
load_dotenv()

# Initialize Nylas client
nylas = Client(
    api_key=os.getenv("NYLAS_API_KEY"),
    api_uri=os.getenv("NYLAS_API_URI")
)

NYLAS_GRANT_ID = os.getenv("NYLAS_GRANT_ID")

def send_email(subject: str, body: str, to_name: str, to_email: str):
    """
    Helper function to send an email using Nylas.
    
    Args:
        subject (str): Email subject.
        body (str): Email body content.
        to_name (str): Recipient's name.
        to_email (str): Recipient's email address.
        
    Returns:
        dict: Sent message data if successful.
        str: Error message if failed.
    """
    try:
        email_payload = {
            "subject": subject,
            "body": body,
            "to": [
                {
                    "name": to_name,
                    "email": to_email
                }
            ]
        }

        message = nylas.messages.send(NYLAS_GRANT_ID, request_body=email_payload).data
        return message

    except Exception as e:
        return str(e)

# URL to fetch predeployed accounts
ACCOUNTS_API = f"{os.getenv("BLOCKCHAIN_API")}/predeployed_accounts"  # Replace with actual API URL

def fetch_and_create_wallets(db: Session):
    # Check if wallets table is empty
    existing_wallets = db.query(Wallet).first()
    if existing_wallets:
        print("Wallets already exist. Skipping creation.")
        return  # Exit the function if wallets already exist

    try:
        response = requests.get(ACCOUNTS_API)
        response.raise_for_status()
        accounts = response.json()

        for account in accounts:
            wallet = Wallet(
                user_id=None,  # Not assigned to any user yet
                account_address=account["address"],
                private_key=account["private_key"],
                public_key=account["public_key"]
            )
            db.add(wallet)
        
        db.commit()
        print(f"Successfully created {len(accounts)} wallets!")

    except Exception as e:
        print(f"Error fetching or creating wallets: {e}")
