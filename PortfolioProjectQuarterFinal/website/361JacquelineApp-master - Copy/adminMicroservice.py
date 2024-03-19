import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError
import zmq

debug = 1

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# this sends updates to users and admin from 361foodapp@gmail.com, password "aidanjacqueline"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)



while True:
    # set up variables for debugging
    response = "invalid command"
    contact = ""
    recipeName = ""
    recipe = ""
    user = ""

    if debug == 1:
        print("ready to receive")
    message = socket.recv()
    messagestr = str(message)
    if debug == 1:
        print("received message: %s" % messagestr)

    # clean up input
    messagestr = messagestr[2:-1]
    if debug == 1:
        print("input selector is: %s" % messagestr[6:11])

    contact = messagestr[messagestr.find("CONTACT") + 9: messagestr.find("; RECIPE NAME")]



    # send a message to admin
    if messagestr[6:11] == "admin":
        if debug == 1:
            print("sending admin message")
        recipeName = messagestr[messagestr.find("RECIPE NAME") + 13: messagestr.find("; RECIPE:")]
        recipe = messagestr[messagestr.find("; RECIPE:") + 9: messagestr.find("; USER:")]
        user = messagestr[messagestr.find("; USER:") + 8:]

        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText('The user ' + user + ' has created a recipe called ' + recipeName + ' and these ingredients \
        and instructions: ' + recipe)
        message['to'] = contact
        message['subject'] = "361 Recipe Project Admin Email"
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        try:
            message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message to {message} Message Id: {message["id"]}')
            response = "sent admin message"
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None

    # send a message to user
    elif messagestr[6:10] == "user":
        if debug == 1:
            print("sending user message")
        recipeName = messagestr[messagestr.find("RECIPE NAME") + 13:]

        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText('Thank you for creating this recipe: ' + recipeName)
        message['to'] = contact
        message['subject'] = "361 Recipe Project Recipe Creation Confirmation"
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        try:
            message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message to {message} Message Id: {message["id"]}')
            response = "sent user message"
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None

    # else proceed - will send "invalid command" response
    else:
        pass
    # free up socket by responding
    if debug == 1:
        print("contact is %s" % contact)
        print("recipeName is %s" % recipeName)
        print("recipe is %s" % recipe)
        print("user is %s" % user)

    if debug == 1:
        print("sending response packet")
    socket.send_string(response)

