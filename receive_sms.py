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
    needshelp = 0

    # !echo
    if check == 1:
        body = body[6:]
        resp.message(body)
        return str(resp)

    # !wiki
    elif check == 2:
        body = body[6:]
        name = wikipedia.suggest(body)
        title = wikipedia.page(name).title
        summary = wikipedia.summary(name, sentences=3)
        url = wikipedia.page(name).title
        wiki_stuff = title + "\n" + summary + "\n" + "Find out more at " + url
        resp.message(wiki_stuff)
        return str(resp)

    elif check == 0:
        helpcheck = body[6:]
        echo = "!echo [YourTextHere] repeats whatever you input"
        wiki = "!wiki [SearchWordHere] displays information about the searched word"
        dumb = "!help [CommandHere] explains each command"
        commandlist = ["echo", "wiki", "help", "all"]
        if helpcheck == "echo":
            resp.message(echo)
            return str(resp)
        elif helpcheck == "wiki":
            resp.message(wiki)
            return str(resp)
        elif helpcheck == "help":
            resp.message(dumb)
            return str(resp)
        elif helpcheck == "all":
            allcommands = "Commands: all, echo, wiki, help" + "\n\n" + echo + "\n\n" + wiki + "\n\n" + dumb
            resp.message(allcommands)
            return str(resp)
        elif helpcheck == "":
            resp.message(commandlist)
            return str(resp)

#    else:
    #    needshelp = needshelp + 1
    #    if needshelp >= 10:
    #        needshelp = 0

    #    return



#Checks for the command
def command_check():
    body = request.values.get('Body', None)
    body = body.lower()
    check = body[:6]
    if check == '!echo ':
        return 1
    elif check == '!wiki ':
        return 2
    elif check == '!help':
        return 0



if __name__ == "__main__":
    app.run(debug=True)
