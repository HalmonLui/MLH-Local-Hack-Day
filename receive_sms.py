# Imports stuff
import os
import wikipedia
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

# Initiates Flask
app = Flask(__name__)

# Sends a request for post and get
@app.route("/sms", methods=['GET', 'POST'])

# Replies
def sms_reply():
    
    # Gets the SMS sent to the number
    body = request.values.get('Body', None)
    check = command_check()
    resp = MessagingResponse()
    
    # !echo
    if check == 1:
        body = body[6:]
        resp.message(body)
        return str(resp)
    
    # !wiki
    elif check == 2:
        param = body[6:].replace(" ", "_")
        wiki_link = "https://en.wikipedia.org/" + param
        resp.message(wiki_link)
        return str(resp)
    
    # Anything else
    else:
        resp.message("Invalid.")
        return str(resp)

#Checks for the command
def command_check():
    body = request.values.get('Body', None)
    body = body.lower()
    check = body[:6]
    if check == '!echo ':
        return 1
    elif check == '!wiki ':
        return 2
    else:
        return 0


if __name__ == "__main__":
    app.run(debug=True)
