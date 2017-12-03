# Imports stuff
import os
import wikipedia
import yahoo_finance
import json
import requests
import random
from yahoo_finance import Share
from helpers import *
from googlefinance import getQuotes
from flask import Flask, request, redirect
from flask import Flask, request, redirect, send_file
from twilio.twiml.messaging_response import MessagingResponse

# Imgur
from imgurpython import ImgurClient
client_id = 'c6304c244358656'
client_secret = 'd810dd4b469ee625098f45efcea34b14c05dfbdb'

# Initiates Flask
app = Flask(__name__)

# Sends a request for post and get
@app.route("/sms", methods=['GET', 'POST'])

# Replies
def sms_reply():

    # Gets the SMS sent to the number
    body = request.values.get('Body', "")
    check = command_check()
    resp = MessagingResponse()
    needshelp = 0

    # !echo
    if check == 1:
        body = body[6:]

        # Checks for parameters
        if body == None:
            resp.message("!echo requires additional input.")
        else:
            resp.message(body)

        # Echoes
        return str(resp)

    # !wiki
    elif check == 2:
        body = body[6:]

        # Checks for parameters
        if body == None:
            resp.message("!wiki requires additonal input.")
            return str(resp)

        # Search for article
        try:
           search = wikipedia.search(body, results=1, suggestion=True)
        except wikipedia.exceptions.PageError as e:
            resp.message("Error generating Wikipedia page.")
            return str(resp)

        # Removes disambiguation error
        try:
            article = wikipedia.page(title=search[0])
        except wikipedia.exceptions.DisambiguationError as e:
            article = wikipedia.page(title=e.options[0])

        # Returns article info
        title = article.title
        summary = wikipedia.summary(title, sentences=3)
        url = article.url

        # Submits article info
        wiki_stuff = title + "\n\n" + summary + "\n\n" + "Find out more at:" + url
        resp.message(wiki_stuff)
        return str(resp)

    # !stock
    elif check == 3:
        body = body[7:]

        # Checks for parameters
        if body == None:
            resp.message("!stock requires additonal input.")

        body = body.upper()
        stocklink = "https://finance.google.com/finance?q=" + body + "&output=json"
        rsp = requests.get(stocklink)

        if rsp.status_code in (200,):
            fin_data = json.loads(rsp.content[6:-2].decode('unicode_escape'))
            openprice = ('Opening Price: ${}'.format(fin_data['op']))
            stockname = ('Stock Name: {}'.format(fin_data['name']))
            stockinfo = stockname + "\n" + "Symbol: " + body + "\n" + openprice
        if format(fin_data['op']) == "":
            stockinfo = "Invalid stock symbol \n\nSymbols: Facebook(FB), Apple(AAPL), Alphabet(GOOG), Yahoo(YHOO), Amazon(AMZN), Coca-Cola(KO), Walmart(WMT), Microsoft(MSFT)\n\nMore at: https://finance.yahoo.com/"
        resp.message(stockinfo)
        return str(resp)

    # !help
    elif check == 0:
        return help()

    # !rand
    elif check == 4:
        body = body[6:]

        # If no parameter is applied
        if body == None:
            items = ImgurClient.gallery()
            randnum = random(0, len(items)-1)
            img = get_image(items[randnum].image_id)
            return img
        else:
            items = ImgurClient.gallery_search(body)
            randnum = random(0, len(items)-1)
            img = get_image(items[randnum].image_id)
            return img


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
    stock = "!stock [Symbol] shows stock opening price"
    commandlist = ["echo", "wiki", "help", "all"]
    resp = MessagingResponse()
    body = request.values.get('Body', None)
    body = body.lower()
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
    elif helpcheck == "stock":
        resp.message(stock)
        return str(resp)
    elif helpcheck == "all":
        allcommands = "Commands: all, echo, wiki, help, stock" + "\n\n" + echo + "\n\n" + wiki + "\n\n" + dumb
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
    elif check == '!stock':
        check = body[:7]
        if check == '!stock ':
            return 3
    elif check == '!help ':
        return 0
    elif check == '!rand ':
        return 4



if __name__ == "__main__":
    app.run(debug=True)
