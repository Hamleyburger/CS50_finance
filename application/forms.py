from flask import session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
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


