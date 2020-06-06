from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User
from .exceptions import invaldPasswordError, userNotFoundError


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
        print("I think the user wants to refresh amount. Amount is: {}".format(form.shares.data))

def validSymbol(form, field):
    print(form.search_button.data)
    #if form.search_button.data:
     #   print("I think user is searching for a symbol. Looking up field data: {}".format(form.search.data))

class BuyForm(FlaskForm):
    search = StringField("Search", id="symbolInput", validators=[validSymbol])
    shares = IntegerField("Shares", id="amountInput", validators=[validBuyAmount])
    search_button = SubmitField("Search", id="symbolBtn")
    shares_button = SubmitField("Refresh", id="amountBtn")
    submit_button = SubmitField("Buy")
