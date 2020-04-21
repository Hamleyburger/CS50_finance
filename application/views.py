from application import app, db
from flask import session, request, redirect, render_template, flash, jsonify
from .helpers import login_required, apology, lookup, usd, getUser, \
    clearSessionKeepFlash, userVerified, createUser
from .models import User, Stock, Owned
from werkzeug.exceptions import default_exceptions, HTTPException, \
    InternalServerError


# Custom filter (this gives an error so I'm commenting it out for now)
# app.jinja_env.filters["usd"] = usd

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    print("beginning of buy function")
    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    cash = user.cash
    
    if request.method == "POST":

        # if POST: try to get dict with lookup:
        
        stockDict = ""
        if "buystock" not in session:
            print("buystock not in session, now ''")
            session["buystock"] = ""
        else:
            if "symbol" in session["buystock"]:
                print("symbol exists. Refreshing stockDict")
                stockDict = lookup(session["buystock"]["symbol"])

        if "stockamount" not in session:
            print("stockamount not in session")
            session["stockamount"] = 1
            print("stockamount was None, now it's {}".format(session["stockamount"]))


        # We have three submit-button - "search" and "buy" and "refresh":
        if request.form.get("submit-button") == "search":
            # User searched for a stock. Lookup returns None if stock symbol exists in API
            search = lookup(request.form.get("symbol"))
            if search:
                # if lookup returned a dict assign it to session
                if session["buystock"] != search:
                    # User searched new stock symbol. Reset stock to buy and amount
                    stockDict = search
                    session["stockamount"] = 1
            else:
                # user typed invalid symbol - flashing "error"
                flash(u"Could not find stock symbol in database", "danger")
                                
        elif request.form.get("submit-button") == "refresh":
            # User refreshed price. Should only work if buystock has a symbol
            flash(u"You refreshed price and amount for {}".format(session["buystock"]["name"]), "success")
            session["stockamount"] = request.form.get("amount")
            session["buystock"] = stockDict
            print("you now wish to buy {} {}".format(session["stockamount"], session["buystock"]))
        else:
            # User decided to buy a stock
            print("User has cash: {:.2f} and wants to buy for {:.2f}".format(cash, float(session["buystock"]["price"]) * float(session["stockamount"])))
            exists = Stock.query.filter_by(name=session["buystock"]["symbol"]).first()
            if not exists:
                stock = Stock(symbol=session["buystock"]["symbol"], name=session["buystock"]["name"])
                db.session.add(stock)
                db.session.commit()

        session["buystock"] = stockDict

        if (float(session["stockamount"]) > 0) and ("price" in session["buystock"]):
            session["buytotal"] = float(session["stockamount"]) * float(session["buystock"]["price"])
            
        return redirect(request.url)

    # method is get
    else:
        print("ur username is {}".format(user.username))
        return render_template("/buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    clearSessionKeepFlash()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        username = request.form.get("username")
        password = request.form.get("password")

        if userVerified(username, password):
            session["user_id"] = userVerified(username, password)
            # Redirect user to home page
            return redirect("/")
        else:
            return apology("invalid username or password", 403)

        # for debugging
        print(session)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # lookup returns a Python dict:
        quoteDict = lookup(request.form.get("symbol"))

        if quoteDict:
            return render_template("/quote.html", quoteDict=quoteDict)
        else:
            flash(u"Could not find stock symbol in database", "danger")
            return redirect(request.url)
    else:
        return render_template("/quote.html", quoteDict="")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user
    # Forget anything user related
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        form = request.form.get

        # Ensure username was submitted
        if not form("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not form("password"):
            return apology("must provide password", 403)

        # Ensure password was confirmed
        elif not form("password-confirm"):
            return apology("must confirm password", 403)

        # Ensure password confirmation matches
        elif form("password") != form("password-confirm"):
            return apology("Passwords didn't match", 403)

        # Check if username is taken
        if getUser(form("username")):
            return apology("username taken", 403)
        else:
            # Insert user and hashed password into database
            createUser(form("username"), form("password"))

            flash(u"You were successfully registered", "success")
            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
