import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessaginResponse


app = Flask(__name__)

@app.route("/sms", methods='GET', 'POST')

def sms_reply():
	resp = MessagingResponse()

	resp.message("Hello, world.")

	return str(resp)

if __name__ == "__main__":
	app.run(debug=True)
