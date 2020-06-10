from application import app
from flask import session, request, redirect, render_template, flash, jsonify, url_for
from .helpers import login_required, apology, lookup, usd, \
    setSessionStock, clearSessionExcept
from .models import User, Stock
from .forms import RegistrationForm, LoginForm, BuyForm, SellForm
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
    return redirect(url_for("sell"))

"""
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
            print("User searched for {}".format(symbol))
            # Refresh stock info and reset amount if new symbol/stock search
            try:
                setSessionStock("buystock", symbol=symbol)
            except Exception as e:
                flash(u"{}".format(e), "danger")


        # REFRESH
        elif action == "refresh":
            # User refreshed amount. Refresh total if amount > 0. Else
            amount = int(request.form.get("shares"))
            try:
                setSessionStock("buystock", session["buystock"]["symbol"], amount=amount)
            except Exception as e:
                flash(u"{}".format(e), "danger")

        # BUY
        else:
            # User decided to buy a stock. Buy and reset "buystock" in session
            try:
                user.buy(session["buystock"]["symbol"], session["buystock"]["amount"])
                flash(u"Purhased {} {}".format(
                    session["buystock"]["amount"], session["buystock"]["name"]), "success")
                print("User bought {} {}".format(session["buystock"]["amount"], session["buystock"]["name"]))
                session["buystock"] = {}
                session["cash"] = user.cash
            except Exception as e:
                flash(f"{e}", "danger")

        # Refresh total (amount is handled )
        print("refresh total")
        if ("price" in session["buystock"]) and ("amount" in session["buystock"]):
            session["buystock"]["total"] = float(
                session["buystock"]["amount"]) * float(session["buystock"]["price"])

        return redirect(request.url)

    # method is get
    else:
        return render_template("/buy.html")
"""

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    form = BuyForm()
    setSessionStock("buystock")

    if request.method == "POST":

        if form.validate_on_submit():
            return redirect(url_for("buy"))
        
        print(form.errors)

    return render_template("/buy.html", form=form)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    
    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    transactions = user.transactions()

    return render_template("history.html", tran=transactions)


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
    """Register user"""
    # Clear session from previous login
    clearSessionExcept("csrf_token", "_flashes")

    form = RegistrationForm()
    if request.method == "POST":
        # use Flask-WTF's validation:
        if form.validate_on_submit():
            # Insert user and hashed password into database
            try:
                User.create(form.username.data, form.password.data)
                flash(f"account created for {form.username.data}!", "success")
                return redirect("/login")
            except Exception:
                flash(u"Something went wrong.", "danger")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Clear session from previous login
    clearSessionExcept("_flashes", "csrf_token")

    form = LoginForm()

    if request.method == "POST":
        # use Flask-WTF's validation:
        if form.validate_on_submit():
            return redirect("/")
        else:
            return render_template("login.html", form=form), 403

    # User GET to get here
    return render_template("login.html", form=form)

"""
@app.route("/sell", methods=["GET"])
@app.route("/sell/<symbol>", methods=["GET", "POST"])
@login_required
#@login_required
def sell(symbol=None):

    #Sell shares of stock
    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    stocks = user.ownedStocks()

    if not symbol:
        # Show a list where user can click and choose symbol form its own collection
        grand_total = 0.0
        for stock in stocks:
            grand_total += float(stock.price * stock.amount)
        grand_total += float(user.cash)

        return render_template("/sell.html", stocks=stocks, grand_total=grand_total)

    else:
        # Check that symbol is in user's owned list
        for stock in stocks:
            if symbol.upper() == stock.symbol.upper():
                # Update "sellstock" and offer to sell
                setSessionStock("sellstock", symbol=symbol)
                session["sellstock"]["total"] = float(
                session["sellstock"]["amount"]) * float(session["sellstock"]["price"])

                # GET offers to sell, POST sells and redirects
                if request.method == "GET":
                    return render_template("/sellform.html", stock=stock)
                elif request.method == "POST":
                    if request.form.get("submit-button") == "refresh":
                        # Refresh amount to sell
                        amount = int(request.form.get("shares"))
                        if amount < 1:
                            flash(u"You must input an amount higher than 0", "danger")
                        elif amount > int(stock.amount):
                            flash(u"You only own {} {} stocks.".format(stock.amount, stock.name), "danger")
                        else:
                            setSessionStock("sellstock", amount=amount)
                    else:
                        # Sell stock of given amount
                        try:
                            print("User is selling {} {}".format(stock.symbol, session["sellstock"]["amount"]))
                            user.sell(stock.symbol, session["sellstock"]["amount"])
                            flash(u"Sold {} items of {}".format(session["sellstock"]["amount"], stock.name), "success")
                            setSessionStock("sellstock", amount=1)
                            session["cash"] = user.cash
                            return redirect(url_for("sell"))

                    
                        except Exception as e:
                            flash(u"{}".format(e), "danger")
                    return redirect(request.url)

        return redirect(url_for("sell"))
"""

@app.route("/sell", methods=["GET"])
@app.route("/sell/<symbol>", methods=["GET", "POST"])
@login_required
#@login_required
def sell(symbol=None):

    """Sell shares of stock"""
    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    stocks = user.ownedStocks()

    if not symbol:
        # Show a list where user can click and choose symbol form its own collection
        grand_total = 0.0
        for stock in stocks:
            grand_total += float(stock.price * stock.amount)
        grand_total += float(user.cash)

        return render_template("/sell.html", stocks=stocks, grand_total=grand_total)

    else:
        # There's a symbol. Render a form for interacting with symbol.
        # Check that symbol is in user's owned list
        for stock in stocks:
            if symbol.upper() == stock.symbol.upper():
                # Update "sellstock" and offer to sell
                setSessionStock("sellstock", symbol=symbol)
                
                print("initiate form. Print form and session.")
                form = SellForm()
                form.owned = stock.amount
                print("amount owned now: {}".format(form.owned))
                print(form)
                print(session)

                # GET offers to sell, POST sells and redirects
                if request.method == "GET":
                    return render_template("/hellform.html", stock=stock, form=form)
                elif request.method == "POST":

                    print(f"form validates to: {form.validate_on_submit()}")
                    print(form.errors)
                    # DEAL WITH REFRESH BUTTON
                    if 1 == 1:
                        print("random code")
                    # DEAL WITH SELL BUTTON
                    else:
                        # Sell stock of given amount
                        try:
                            print("User is selling {} {}".format(stock.symbol, session["sellstock"]["amount"]))
                            user.sell(stock.symbol, session["sellstock"]["amount"])
                            flash(u"Sold {} items of {}".format(session["sellstock"]["amount"], stock.name), "success")
                            setSessionStock("sellstock", amount=1)
                            session["cash"] = user.cash
                            return redirect(url_for("sell"))

                    
                        except Exception as e:
                            flash(u"{}".format(e), "danger")


                    # in any case return self
                    return redirect(request.url)

        return redirect(url_for("sell"))






def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
