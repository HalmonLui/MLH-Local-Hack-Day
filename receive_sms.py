import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])


def sms_reply():
    body = request.values.get('Body', None)
    check = command_check()
    resp = MessagingResponse()
    if check == True:
        body = body[5:]
        resp.message(body)
        return str(resp)

def help():

def command_check():
    body = request.values.get('Body', None)
    body = body.lower()
    check = body[:5]
    if check == '!echo':
        return True
    elif check == '!help':
        return True
    else:
        return False


if __name__ == "__main__":
    app.run(debug=True)
