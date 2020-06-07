from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
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
    if form.shares_button.data:
        # User refreshed amount. Refresh total if amount > 0. Else
        amount = field.data
        print("field data amount: {}".format(field.data))
        user = User.query.filter_by(id=session["user_id"]).first()
        if user.cash > float(2000):
            try:
                setSessionStock(keyString="buystock", amount=amount)
            except zeroTransactionError as e:
                raise ValidationError(e)
        else:
            raise ValidationError("Yown less than 2000")


def validSymbol(form, field):
    if form.search_button.data:
        print("pressed search button")
        if form.search.data == "":
            print("You are not searching for anything")
            raise ValidationError("Search field empty")
        else:
            try:
                setSessionStock("buystock", symbol=form.search.data)
            except invalidSymbolError as e:
                raise ValidationError(u"{}".format(e))
    #raise ValidationError("hi in search field")
    #if form.search_button.data:
     #   print("I think user is searching for a symbol. Looking up field data: {}".format(form.search.data))

class BuyForm(FlaskForm):
    search = StringField("Search", id="symbolInput", validators=[validSymbol])
    search_button = SubmitField("Search", id="symbolBtn")
    shares = IntegerField("Shares", id="amountInput", validators=[validBuyAmount])
    shares_button = SubmitField("Refresh", id="amountBtn")
    submit_button = SubmitField("Buy")
