from application import app
from flask import session, request, redirect, render_template, flash, jsonify
from .helpers import login_required, apology, lookup, usd, getUser, \
    clearSessionKeepFlash, userVerified, createUser
from .models import User
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

    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    cash = user.cash
    
    if request.method == "POST":

        # if POST: try to get dict with lookup:
        stockDict = lookup(request.form.get("symbol"))
        if "stockamount" not in session:
            print("stockamount not in session")
            session["stockamount"] = 0
            print("stockamount was None, now it's {}".format(session["stockamount"]))

        # if dict has been returned, do something with it, otherwise flash "error"
        if stockDict:

            # Since dict exists we will have gotten a "name"
            stockName = stockDict["name"]

            # We have three submit-button - "search" and "buy" and "refresh":
            if request.form.get("submit-button") == "search":
                # User searched for a stock
                flash(u"You searched for {}".format(stockName), "success")
                if stockDict:
                    print("stockDict extsts: {}".format(stockDict))
                    session["buystock"] = stockDict
                print("you now wish to buy {} {}".format(session["stockamount"], session["buystock"]))
                return render_template("/buy.html", stockDict=stockDict)
            elif request.form.get("submit-button") == "refresh":
                # User refreshed price
                flash(u"You refreshed price for {}".format(stockName), "success")
                session["stockamount"] = request.form.get("amount")
                print("you now wish to buy {} {}".format(session["stockamount"], session["buystock"]))
                return render_template("/buy.html", stockDict=stockDict)
            else:
                # User decided to buy a stock
                print("you bought {} items of {}".format(session["stockamount"], session["buystock"]))
                return redirect(request.url)

        # user typed invalid symbol - flashing "error"
        else:
            flash(u"Could not find stock symbol in database", "danger")
            return redirect(request.url)
    # method is get
    else:
        print("ur username is {}".format(user.username))
        return render_template("/buy.html", stockDict="")


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
