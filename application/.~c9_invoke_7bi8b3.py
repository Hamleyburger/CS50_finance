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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    user = User.get(user_id=session["user_id"])
    stock = None
    setSessionStock("buystock")

    if "symbol" in session["buystock"]:
        stock = Stock.get(session["buystock"]["symbol"])
        print("stock set to: {}".format(stock.name))
    
    # Stock will be None unless search has been made. But user won't get option to do anything with stock unless there's been a search.
    form = BuyForm(user=user, stock=stock)

    if request.method == "POST":

        if form.validate_on_submit():
            return redirect(url_for("buy"))

        print(form.errors)

    return render_template("/buy.html", form=form)


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
        # calculate grand total of shares + cash
        grand_total = 0.0
        for stock in stocks:
            grand_total += float(stock.price * stock.amount)
        grand_total += float(user.cash)

        return render_template("/sell.html", stocks=stocks, grand_total=grand_total)

    else:
        # There's a symbol. Render a form for interacting with symbol if it exists in "owned list"
        for stock in stocks:
            if symbol.upper() == stock.symbol.upper():
                # Update "sellstock" dict (containing temporary info about the stock in question)
                setSessionStock("sellstock", symbol=symbol)

                form = SellForm(user=user, stock=stock)

                # if POST user clicked either refresh or sell. Forms.py deals with it in validators.
                if request.method == "POST":

                    if form.validate_on_submit():
                        # Each button in form has a validator that refreshes or sells.
                        return redirect(request.url)

                    # form couldn't validate
                    print(form.errors)
                    return render_template("sellform.html", stock=stock, form=form)

                # If method wasn't POST it's get:
                return render_template("/sellform.html", stock=stock, form=form)

        # IF there was a symbol but we didn't find it in our "owned" list:
        return redirect(url_for("sell"))


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


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    transactions = user.transactions()

    return render_template("history.html", tran=transactions)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
