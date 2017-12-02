# Imports stuff
import os
import wikipedia
import yahoo_finance
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
        search = wikipedia.search(body, results = 1, suggestion=True)
        article = wikipedia.page(title=search[0], auto_suggest=True, redirect=True)
        title = article.title
        summary = wikipedia.summary(title, sentences=3)
        url = article.url
        wiki_stuff = title + "\n" + summary + "\n" + "Find out more at " + url
        resp.message(wiki_stuff)
        return str(resp)

    # !stock
    elif check == 3:
        body = body[7:]
        body = body.upper()
        stock = Share(body)
        stock.refresh()
        stockname = stock.get_name()
        openprice = stock.get_open()
        currentprice = stock.get_price()
        stockinfo = "Name: " + stockname + "\n" + "Open Price: " + openprice + "\n" + "Current Price: " + currentprice + "\n"
        resp.message(stockinfo)
        return str(resp)
    # !help
    elif check == 0:
        help()

    # 5 Failed Commands = !help
    else:
        needshelp = needshelp + 1
        if needshelp >= 5:
            needshelp = 0
            help()
        return

#Command Help
def help():
    echo = "!echo [YourTextHere] repeats whatever you input"
    wiki = "!wiki [SearchWordHere] displays information about the searched word"
    dumb = "!help [CommandHere] explains each command"
    commandlist = ["echo", "wiki", "help", "all"]
    helpcheck = body[6:]
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

#Checks for the command
def command_check():
    body = request.values.get('Body', None)
    body = body.lower()
    check = body[:6]
    if check == '!echo ':
        return 1
    elif check == '!wiki ':
        return 2
    elif check == '!stock ':
        return 3
    elif check == '!help':
        return 0



if __name__ == "__main__":
    app.run(debug=True)
