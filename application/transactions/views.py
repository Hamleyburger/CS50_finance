from flask import session, request, redirect, render_template, flash, url_for
from application.main.helpers import login_required
from .helpers import lookup, setSessionStock
from application.models import User, Stock
from .forms import BuyForm, SellForm
from flask import Blueprint

transactions = Blueprint("transactions", __name__)


@transactions.route("/buy", methods=["GET", "POST"])
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
            return redirect(url_for("transactions.buy"))

        print(form.errors)

    return render_template("/buy.html", form=form)


@transactions.route("/sell", methods=["GET"])
@transactions.route("/sell/<symbol>", methods=["GET", "POST"])
@login_required
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

                # If method was GET or form didn't validate:
                return render_template("/sellform.html", stock=stock, form=form)

        # IF there was a symbol but we didn't find it in our "owned" list:
        return redirect(url_for("transactions.sell"))


@transactions.route("/quote", methods=["GET", "POST"])
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


@transactions.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user = User.query.filter_by(id=session["user_id"]).first_or_404()
    transactions = user.transactions()

    return render_template("history.html", tran=transactions)
