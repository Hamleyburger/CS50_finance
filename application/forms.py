from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User
from .helpers import setSessionStock
from .exceptions import invaldPasswordError, userNotFoundError, invalidSymbolError, zeroTransactionError


def uniqueUser(form, field):
    if User.get(field.data):
        raise ValidationError('Username is already taken')


def validPassword(form, field):
    """ Logs user in if valid """
    if not form.username.errors:
        try:
            user = User.verify(form.username.data, field.data)
            session["user_id"] = user.id
            session["username"] = user.username
            session["cash"] = user.cash
        except invaldPasswordError:
            raise ValidationError("Invalid password")


def existingUser(form, field):
    if not User.get(field.data):
        raise ValidationError('User does not exist')


class RegistrationForm(FlaskForm):
    # First argument will be name and will be used as label
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=30), uniqueUser])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), Length(min=8, max=30), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    # First argument will be name and will be used as label
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=4, max=30), existingUser])
    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=8, max=30), validPassword])
    # 'remember me' is currently not being put tu use
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


def validBuyAmount(form, field):
    if form.shares_button.data or form.buy_button.data:
        # User refreshed amount either buy refresh or buy btn. Refresh if > 0 and user can afford
        amount = form.shares.data
        print(f"amount {amount}")
        user = form.user
        print(f"user {user}")
        print(f"stock {form.stock}")

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
                print("User bought {} {}".format(session["buystock"]["amount"], stock.name))
                session["buystock"] = {}
                session["cash"] = user.cash
            except Exception as e:
                flash(f"{e}", "danger")
                raise ValidationError(e)


class BuyForm(FlaskForm):
    search = StringField("Search", id="symbolInput", render_kw={"placeholder": "Search for symbol"}, validators=[validSymbol])
    search_button = SubmitField("Search")
    shares = IntegerField("Shares", id="amountInput", default=1, validators=[validBuyAmount])
    shares_button = SubmitField("Refresh")
    buy_button = SubmitField("Buy", validators=[allowBuy])

    def __init__(self, user, stock, *args, **kwargs):
        super(BuyForm, self).__init__(*args, **kwargs)
        self.user = user
        self.stock = stock
        print("initiated and set user to {}".format(user.username))


def validSellAmount(form, field):

    if form.shares_button.data:
        print("refresh btn pressed")
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
        print("allowSell recognzes {} as user".format(user.username))
        try:
            print("User is selling {} {}".format(stock.symbol, session["sellstock"]["amount"]))
            user.sell(stock.symbol, session["sellstock"]["amount"])
            flash(u"Sold {} items of {}".format(session["sellstock"]["amount"], stock.name), "success")
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
        print("initiated and set user to {}".format(user))