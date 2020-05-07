from application import app
from flask import session, request, redirect, render_template, flash, jsonify, url_for
from .helpers import login_required, apology, lookup, usd, \
    clearSessionKeepFlash, setSessionStock
from .dbhelpers import userVerified
from .models import User
from .forms import RegistrationForm, LoginForm
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

    if request.method == "POST":

        user = User.query.filter_by(id=session["user_id"]).first_or_404()
        # action can be search, refresh (amount) or buy
        action = request.form.get("submit-button")
        # setSessionStock initiates or refreshes session stock info
        setSessionStock("buystock")

        # SEARCH
        if action == "search":

            symbol = request.form.get("symbol")
            if lookup(symbol):
                # Refresh stock info and reset amount if new symbol/stock search
                setSessionStock("buystock", symbol=symbol)
            else:
                flash(u"Invalid stock symbol", "danger")

        # REFRESH
        elif action == "refresh":
            # User refreshed amount. Refresh total if amount > 0. Else
            amount = int(request.form.get("amount"))
            if amount > 0:
                setSessionStock("buystock", amount=amount)
            else:
                flash(u"You must input an amount higher than 0", "danger")

        # BUY
        else:
            # User decided to buy a stock. Buy and reset "buystock" in session
            if user.buy(session["buystock"]["symbol"], session["buystock"]["amount"]):
                flash(u"Purhased {} {}".format(
                    session["buystock"]["amount"], session["buystock"]["name"]), "success")
                session["buystock"] = {}
                session["cash"] = user.cash
            else:
                flash("Something went wrong")

        # Refresh total (amount is handled )
        if ("price" in session["buystock"]) and ("amount" in session["buystock"]):
            session["buystock"]["buytotal"] = float(
                session["buystock"]["amount"]) * float(session["buystock"]["price"])

        return redirect(request.url)

    # method is get
    else:
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
            # Redirect user to home page
            return redirect("/")
        else:
            return apology("invalid username or password", 403)

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
        if User.get(form("username")):
            return apology("username taken", 403)
        else:
            # Insert user and hashed password into database
            User.create(form("username"), form("password"))

            flash(u"You were successfully registered", "success")
            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/registur", methods=["GET", "POST"])
def registur():
    # Register user
    # Forget anything user related
    print(session)

    form = RegistrationForm()
    print("form.validate is {}".format(form.validate_on_submit()))
    if form.validate_on_submit():
        flash(f"account created for {form.username.data}!", "success")
        return redirect(url_for("login"))

    return render_template("registur.html", form=form)


@app.route("/lugin", methods=["GET", "POST"])
def lugin():
    """Log user in"""

    # Forget any user_id
    clearSessionKeepFlash()

    form = LoginForm()
    return render_template("lugin.html", title="Login", form=form)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    """TODO: 
    if get:
        define a list of owned stocks containing: Symbol, name, price, amount owned
        render template sell
    if post:
        search must be searching list of owned stocks for filtering
        search can redefine the list which will only be reset at get or after sell.
        search does NOT define what stock is being sold.
        clicking an item opens a sell modal.
        make a "reset search" button

        Sell dialogue (like buy stock):
        refresh: refreshes amount of sell stocks
        sell button sells.
    """

    if request.method == "POST":

        user = User.query.filter_by(id=session["user_id"]).first_or_404()
        # action can be search, refresh (amount) or sell
        action = request.form.get("submit-button")
        # setSessionStock initiates or refreshes session stock info
        setSessionStock("sellstock")

        # SEARCH
        if action == "search":

            symbol = request.form.get("symbol")
            if lookup(symbol):
                # Refresh stock info and reset amount if new symbol/stock search
                setSessionStock("sellstock", symbol=symbol)
            else:
                flash(u"Invalid stock symbol", "danger")

        # REFRESH
        elif action == "refresh":
            # User refreshed amount. Refresh total if amount > 0. Else
            amount = int(request.form.get("amount"))
            if amount > 0:
                setSessionStock("sellstock", amount=amount)
            else:
                flash(u"You must input an amount higher than 0", "danger")

        # SELL
        else:
            # User decided to sell a stock. Sell and reset "sellstock" in session
            if user.sell(session["sellstock"]["symbol"], session["sellstock"]["amount"]):
                flash(u"Sold {} {}".format(
                    session["sellstock"]["amount"], session["sellstock"]["name"]), "success")
                session["sellstock"] = {}
                session["cash"] = user.cash
            else:
                flash("Something went wrong")

        # Refresh total (amount is handled )
        if ("price" in session["sellstock"]) and ("amount" in session["sellstock"]):
            session["sellstock"]["selltotal"] = float(
                session["sellstock"]["amount"]) * float(session["sellstock"]["price"])

        return redirect(request.url)

    # method is get
    else:
        return render_template("/sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
