from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from time import gmtime, strftime

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    
    # stray code in case I lock myself out when testing
    ## session.clear()
    ## return redirect(url_for("login"))
    
    # stores empty dicts
    stock_data = {}
    user_data = {}
    
    # stores values for future use
    dict_count = 0
    share_value = 0
    stock_count = 0
    
    # get stocks dict and user info dict
    stocks = db.execute("SELECT * FROM stocks WHERE id = :id", id=session["user_id"])
    
    # stores user info
    users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        
    # ensure user info is correct
    if len(users) != 1:
        return apology("error when accessing user information", "account may have been compromised")
    else:
        user = users[0]
    
    # iterate for every stock on the user's portfolio
    for stock in stocks:
        
        # empty dict
        stock_data["dict{0}".format(dict_count)] = {}
        
        # stores stock symbol
        stock_data["dict{0}".format(dict_count)]["symbol"] = stock["symbol"]
        
        # stock info for future use
        stock_info = lookup(stock["symbol"])
        
        # stores current price and number of shares
        stock_data["dict{0}".format(dict_count)]["price"] = usd(stock_info["price"])
        stock_data["dict{0}".format(dict_count)]["shares"] = stock["shares"]
        
        # stores total value of all shares
        total = float(stock["shares"] * float(stock_info["price"]))
        stock_data["dict{0}".format(dict_count)]["total"] = usd(total)
        
        # future use
        share_value += total
        dict_count += 1
    
    # stores miscellaneous values
    user_data["curr_balance"] = usd(float(user["cash"]))
    user_data["total"] = usd(float(user["cash"]) + float(share_value))
    user_data["numstocks"] = dict_count
    
    # creates table of information
    return render_template("index.html", data=(stock_data, user_data))

@app.route("/trade", methods=["GET", "POST"])
@login_required
def trade():
    """Trade shares of stock."""

     # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # gets information for the stock
        stock = lookup(request.form.get("symbol"))
	
        # gets action requested
        action = request.form.get("action")
	
        # ensure stock exists
        if not stock:
            return apology("error when looking up stock", "make sure you put in stock symbol correctly")
        
        # gets number of shares
        shares = request.form.get("shares")
        
        # ensures number of shares is positive integer
        if not int(shares) >= 1:
	        if action == "buy":
		        return apology("please buy a valid number of shares")
	        elif action == "sell":
		        return apology("please sell a valid number of shares")
	        else:
		        return apology("error processing request")
        
        # stores user info
        users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        stocks = db.execute("SELECT * FROM stocks WHERE id = :id AND symbol=:symbol", id=session["user_id"], symbol=stock["symbol"])
        
        # ensure user info is correct
        if len(users) != 1:
            return apology("error when accessing user information", "account may have been compromised")
        else:
            user = users[0]
        
        # ensures user has enough money to buy the shares
        if action == "buy" and user["cash"] < (stock["price"] * float(shares)):
            return apology("insufficient cash to buy shares")
        
        # ensures user has sufficient shares to sell
        if action == "sell" and int(shares) > int(stocks[0]["shares"]):
            return apology("not enough shares to sell")
        
        if action == "buy":
	        # creates new field if one does not exist
	        if not stocks:
	            change_shares = db.execute("INSERT INTO stocks (id, symbol, shares) VALUES (:id, :symbol, :shares)", id=session["user_id"], symbol=stock["symbol"], shares=shares)
	        # updates if one does exist
	        else:
		        change_shares = db.execute("UPDATE stocks SET shares = :shares WHERE id = :id AND symbol = :symbol", shares=int(stocks[0]["shares"])+int(shares), id=session["user_id"], symbol=stocks[0]["symbol"])
        else:
            change_shares = db.execute("UPDATE stocks SET shares = :shares WHERE id = :id AND symbol = :symbol", shares=int(stocks[0]["shares"])-int(shares), id=session["user_id"], symbol=stocks[0]["symbol"])
	
        # ensure shares are sold correctly
        if not change_shares:
            if action == "buy":
                return apology("error when buying shares")
            else:
                return apology("error when selling shares")
        
        # changes cash
        if action == "buy":
            change_cash = db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=float(user["cash"]-(stock["price"] * float(shares))), id=session["user_id"])
        else:
            change_cash = db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=float(user["cash"]+(stock["price"] * float(shares))), id=session["user_id"])
        
        # ensure cash is updated correctly
        if not change_cash:
            return apology("error when updating databases")
        
        # stores sell data into transaction history
        if action == "buy":
            result = db.execute("INSERT INTO transactions (id, datetime, symbol, shares, price, balance, type) VALUES (:id, :datetime, :symbol, :shares, :price, :balance, :type)", id=session["user_id"], datetime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), symbol=stock["symbol"], shares=shares, price=stock["price"],  balance=float(user["cash"]-(stock["price"] * float(shares))), type="BUY")
        else:
            result = db.execute("INSERT INTO transactions (id, datetime, symbol, shares, price, balance, type) VALUES (:id, :datetime, :symbol, :shares, :price, :balance, :type)", id=session["user_id"], datetime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), symbol=stock["symbol"], shares=shares, price=stock["price"],  balance=float(user["cash"]-(stock["price"] * float(shares))), type="SELL")
        
        # ensure transaction data is stored
        if not result:
            return apology("error when updating databases")
        
        # redirects back to main page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("trade.html")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Show history of transactions."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # gets transaction history
        if request.form["order"] == "DESC":
            transactions = db.execute("SELECT * FROM transactions WHERE id=:id ORDER BY datetime DESC", id=session["user_id"])
        else:
            transactions = db.execute("SELECT * FROM transactions WHERE id=:id ORDER BY datetime ASC", id=session["user_id"])
        
        # ensure that transaction history can be obtained
        if not transactions:
            return apology("trouble getting transaction history", "please try again later")
        
        # changes everything to format usd
        for i in range(len(transactions)):
            price = transactions[i]["price"]
            transactions[i]["price"] = usd(price)
            
            balance = transactions[i]["balance"]
            transactions[i]["balance"] = usd(balance)
        
        history = (transactions, len(transactions))
        
        # redirect user to history
        return render_template("historied.html", history=history)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("history.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    
    """Get stock quote."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # gets quote
        quote = lookup(request.form.get("symbol"))
        
        # ensure stock exists
        if not quote:
            return apology("error when looking up stock", "make sure you put in stock symbol correctly")
        
        quotey = {}
        quotey["name"] = quote["name"]
        quotey["symbol"] = quote["symbol"]
        quotey["price"] = usd(quote["price"])

        # redirect user to quote
        return render_template("quoted.html", quotex=quotey)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    # forget any user_id
    session.clear()
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("please input username")
        
        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("please input password")
        
        # ensure password was confirmed
        elif not request.form.get("confirmation"):
            return apology("please confirm password")
        
        # ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")
        
        # hashes password
        hash=pwd_context.encrypt(request.form.get("password"))
        
        # insert username and hash of password into database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=hash)
        
        # ensure username wasn't already taken
        if not result:
            return apology("username already taken")
        
        # stores user info
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        
        # ensure user info is correct
        if len(rows) != 1:
            return apology("error when accessing user information", "account may have been compromised")
        else:
            user = rows[0]
        
        # creates deposit for user upon registration
        result = db.execute("INSERT INTO transactions (id, datetime, symbol, shares, price, balance, type) VALUES (:id, :datetime, :symbol, :shares, :price, :balance, :type)", id=user["id"], datetime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), symbol="CASH**", shares=user["cash"], price=1, balance=user["cash"], type="DEPOSIT")
        
        # ensure transaction data is stored
        if not result:
            return apology("error with initial deposit")
        
        # redirect user to login form
        return redirect(url_for("login"))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    """Transfer money in/out of the account."""
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # gets dollar amount to deposit/withdraw
        amount = request.form.get("amount")
        
        # gets action requested
        action = request.form.get("action")
        
        # ensures amount deposited/withdrawn is positive integer
        if not float(amount) >= 0:
            
            if action == "deposit":
                return apology("please deposit a valid amount")
            
            elif action == "withdraw":
                return apology("please withdraw a valid amount")
            
            else:
                return apology("error processing request")
        
        # stores user info
        users = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        
        # ensure user info is correct
        if len(users) != 1:
            return apology("error when accessing user information", "account may have been compromised")
        else:
            user = users[0]
        
        # ensures user has sufficient shares to sell
        if action == "withdraw" and float(user["cash"]) < float(amount):
            return apology("insufficient money to withdraw")
        
        # changes cash
        if action == "deposit":
            change_cash = db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=float(user["cash"]+float(amount)), id=session["user_id"])
        else:
            change_cash = db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=float(user["cash"]-float(amount)), id=session["user_id"])
        
        # ensure cash is updated correctly
        if not change_cash:
            return apology("error when updating databases")
        
        # stores sell data into transaction history
        if action == "deposit":
            result = db.execute("INSERT INTO transactions (id, datetime, symbol, shares, price, balance, type) VALUES (:id, :datetime, :symbol, :shares, :price, :balance, :type)", id=session["user_id"], datetime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), symbol="CASH**", shares=amount, price=1,  balance=float(user["cash"]+float(amount)), type="DEPOSIT")
        else:
            result = db.execute("INSERT INTO transactions (id, datetime, symbol, shares, price, balance, type) VALUES (:id, :datetime, :symbol, :shares, :price, :balance, :type)", id=session["user_id"], datetime=strftime("%Y-%m-%d %H:%M:%S", gmtime()), symbol="CASH**", shares=amount, price=1,  balance=float(user["cash"]-float(amount)), type="WITHDRAW")
        
        # ensure transaction data is stored
        if not result:
            return apology("error when updating databases")
        
        # redirects back to main page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("transfer.html")
    
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    
    """Lets user change password."""
    
    # stores user info
    users = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
        
    # ensure user info is correct
    if len(users) != 1:
        return apology("error when accessing user information", "account may have been compromised")
    else:
        user = users[0]
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # ensure password was submitted
        if not request.form.get("password"):
            return apology("please input current password")
        
        # ensure new password was submitted
        elif not request.form.get("password_new"):
            return apology("please input new password")
        
        # ensure password was confirmed
        elif not request.form.get("confirmation"):
            return apology("please confirm new password")
        
        # ensure the user put in correct password
        elif not pwd_context.verify(request.form.get("password"), user["hash"]):
            return apology("incorrect password")
        
        # ensure same password was not attempted to be used
        elif pwd_context.verify(request.form.get("password_new"), user["hash"]):
            return apology("please do not reuse old password")
        
        # ensure password and confirmation match
        elif request.form.get("password_new") != request.form.get("confirmation"):
            return apology("passwords do not match")
        
        # hashes password
        hash=pwd_context.encrypt(request.form.get("password_new"))
        
        # insert username and hash of password into database
        result = db.execute("UPDATE users SET hash=:hash WHERE username=:username AND id=:id", hash=hash, username=user["username"], id=session["user_id"])
        
        # ensure username wasn't already taken
        if not result:
            return apology("error updating user password", "please try again later")
        
        # redirect user to index
        return redirect(url_for("index"))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        
        return render_template("account.html", user=user)