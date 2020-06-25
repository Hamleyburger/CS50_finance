from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import ValidationError
from application.models import User
from .helpers import setSessionStock
from application.exceptions import invalidSymbolError, zeroTransactionError


def validBuyAmount(form, field):
    if form.shares_button.data or form.buy_button.data:
        # User refreshed amount either buy refresh or buy btn. Refresh if > 0 and user can afford
        amount = form.shares.data
        user = form.user

        canAfford = False

        try:
            canAfford = (float(user.cash) > (float(amount) * form.stock.price))
        except Exception:
            raise ValidationError("Something is not right. Try reloading.")

        if canAfford:
            try:
                setSessionStock(keyString="buystock", amount=amount)
            except zeroTransactionError as e:
                raise ValidationError(e)

            except Exception:
                raise ValidationError("Unknown error")
        else:
            raise ValidationError("Can't afford!")


def validSymbol(form, field):
    if form.search_button.data:
        if form.search.data == "":
            raise ValidationError("Search field empty")
        else:
            try:
                setSessionStock("buystock", symbol=form.search.data)
            except invalidSymbolError as e:
                raise ValidationError(u"{}".format(e))


def allowBuy(form, field):
    if form.buy_button.data:
        user = User.query.filter_by(id=session["user_id"]).first()
        stock = form.stock

        # Only try selling if amount of shares is validated
        if not form.shares.errors:
            try:
                user.buy(stock.symbol, session["buystock"]["amount"])
                flash(u"Purhased {} {}".format(
                    session["buystock"]["amount"], stock.name), "success")
                print("{} bought {} {}".format(user.username,
                                               session["buystock"]["amount"], stock.name))
                session["buystock"] = {}
                session["cash"] = user.cash
            except Exception as e:
                flash(f"{e}", "danger")
                raise ValidationError(e)


class BuyForm(FlaskForm):
    search = StringField("Search", id="symbolInput", render_kw={
                         "placeholder": "Search for symbol"}, validators=[validSymbol])
    search_button = SubmitField("Search")
    shares = IntegerField("Shares", id="amountInput",
                          default=1, validators=[validBuyAmount])
    shares_button = SubmitField("Refresh")
    buy_button = SubmitField("Buy", validators=[allowBuy])

    def __init__(self, user, stock, *args, **kwargs):
        super(BuyForm, self).__init__(*args, **kwargs)
        self.user = user
        self.stock = stock


def validSellAmount(form, field):

    if form.shares_button.data:
        # Refresh amount to sell
        amount = field.data
        stock = form.stock
        owned = stock.amount

        if amount > owned:
            raise ValidationError("You only own {}".format(owned))

        try:
            setSessionStock("sellstock", amount=amount)
        except Exception as e:
            raise ValidationError(e)


def allowSell(form, field):
    if field.data:
        user = form.user
        stock = form.stock
        try:
            print("{} is selling {} {}".format(user.username,
                                               stock.symbol, session["sellstock"]["amount"]))
            user.sell(stock.symbol, session["sellstock"]["amount"])
            flash(u"Sold {} items of {}".format(
                session["sellstock"]["amount"], stock.name), "success")
            setSessionStock("sellstock", amount=1)
            session["cash"] = float(user.cash)

        except Exception as e:
            flash(u"{}".format(e), "danger")
            raise ValidationError(e)


class SellForm(FlaskForm):

    shares = IntegerField("Shares", default=1, validators=[validSellAmount])
    shares_button = SubmitField("Refresh")
    sell_button = SubmitField("Sell", validators=[allowSell])

    def __init__(self, user, stock, *args, **kwargs):
        super(SellForm, self).__init__(*args, **kwargs)
        self.user = user
        self.stock = stock
