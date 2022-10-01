from __future__ import print_function
from bs4 import BeautifulSoup
from urlextract import URLExtract
import base64
import email
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    extractor = URLExtract()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        #results = service.users().labels().list(userId='me').execute()
        #labels = results.get('labels', [])
        
        results = service.users().messages().list(userId='me', labelIds=['Label_538763522493983273'], q="is:unread").execute()
        messages = results.get('messages', [])

        if not messages:
            print("No new messages")
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                
                payload = msg['payload']
                email_data = payload['headers']

                parts = payload.get('parts')

                for part in parts:
                    body = part.get("body")
                    data = body.get("data")
                    mimeType = part.get("mimeType")
                    
                    # with attachment
                    if mimeType == 'multipart/related':
                        subparts = part.get('parts')
                        for p in subparts:
                            body = p.get("body")
                            data = body.get("data")
                            mimeType = p.get("mimeType")
                            if mimeType == 'text/plain':
                                body_message = base64.urlsafe_b64decode(data)
                            elif mimeType == 'text/html':
                                body_message = base64.urlsafe_b64decode(data)

                    
                    # without attachment
                    elif mimeType == 'text/plain':
                        body_message = base64.urlsafe_b64decode(data)
                    elif mimeType == 'text/html':
                        body_message = base64.urlsafe_b64decode(data)

                final_result = str(body_message, 'utf-8')

                url = extractor.find_urls(final_result)
                print(url[0])

                for values in email_data:
                    name = values["name"]

                    if name == "From":
                        from_name = values["value"]
                        print(from_name)

                service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                

                
                
        

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()