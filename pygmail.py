import tkinter as tk
from tkinter import messagebox, Toplevel
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
from requests import HTTPError
from email import message_from_bytes
import webbrowser

# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",  # Scope to read emails
]

# Global variables for credentials and service
creds = None
service = None

def authenticate():
    """Authenticate with Gmail API and return the service object."""
    global creds, service
    if creds is not None:
        return service  # If already authenticated, skip re-authentication

    try:
        # Check if token.pickle exists and load credentials from there
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If credentials are invalid or expired, reauthorize
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Refresh the credentials if expired
            else:
                # If no valid credentials, start the OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)  # This will open the auth page

            # Save the credentials for the next session
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Build the service after authentication
        service = build('gmail', 'v1', credentials=creds)
        return service

    except Exception as e:
        messagebox.showerror("Authentication Error", f"Failed to authenticate:\n{e}")
        print(e)
        raise e

def send_email(to_list, subject, body):
    """Sends an email using Gmail API to multiple recipients in a single message."""
    try:
        service = authenticate()  # Authenticate or get existing service
        
        # Build the email
        message = MIMEText(body)
        message['to'] = ", ".join(to_list)  # Combine recipients into a single string
        message['subject'] = subject
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        # Send the email
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Email sent: {sent_message}")
        return True

    except HTTPError as error:
        messagebox.showerror("Error", f"An error occurred while sending the email:\n{error}")
        print(error)
        raise error

# GUI Frontend
def send_email_gui():
    """Handles the email sending process triggered by the GUI button."""
    recipients = entry_recipient.get()
    subject = entry_subject.get()
    body = text_body.get("1.0", tk.END).strip()  # Get text from the body text widget
    
    if not recipients or not subject or not body:
        messagebox.showwarning("Missing Information", "Please fill in all fields.")
        return

    # Split the recipient emails by commas
    recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]
    
    if not recipient_list:
        messagebox.showwarning("Invalid Emails", "Please provide valid email addresses.")
        return

    try:
        send_email(recipient_list, subject, body + "\nSent from Python")
        messagebox.showinfo("Success", "Email sent successfully to all recipients!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while sending the email:\n{e}")
        print(e)

def view_emails():
    webbrowser.open("https://mail.google.com/mail/u/0/#inbox")

# Initialize Tkinter root window
root = tk.Tk()
root.title("Email Sender")

# Create widgets
tk.Label(root, text="Recipient Emails (comma-separated):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_recipient = tk.Entry(root, width=50)
entry_recipient.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Subject:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_subject = tk.Entry(root, width=50)
entry_subject.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Message Body:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
text_body = tk.Text(root, width=50, height=10)
text_body.grid(row=2, column=1, padx=10, pady=5)

send_button = tk.Button(root, text="Send Email", command=send_email_gui)
send_button.grid(row=3, column=0, columnspan=2, pady=10)

view_button = tk.Button(root, text="View Emails", command=view_emails)
view_button.grid(row=4, column=0, columnspan=2, pady=10)

# Start the Tkinter event loop
root.mainloop()
