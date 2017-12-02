import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])


def sms_reply():
    body = request.values.get('Body', None)
    check = command_check()
    resp = MessagingResponse()
    if check == 1:
        body = body[6:]
        resp.message(body)
        return str(resp)
    elif check == 2:
        param = body[6:].replace(" ", "_")
        wiki_link = "https://en.wikipedia.org/" + param
        resp.message(wiki_link)
        return str(resp)
    else:
        resp.message("Invalid.")
        return str(resp)

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
