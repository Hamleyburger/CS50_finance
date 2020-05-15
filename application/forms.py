from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User


def uniqueUser(form, field):
    if User.get(field.data):
        print("uniqueUser failed")
        raise ValidationError('Sorry. That name is already taken')


class RegistrationForm(FlaskForm):
    # First argument will be name and will be used as label
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=30), uniqueUser])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), Length(min=8, max=30), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    # First argument will be name and will be used as label
    username = StringField("Username", validators=[
                           DataRequired(), Length(min=4, max=30)])
    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=8, max=30)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")

    """
    title:
    Register

form action="/register
        <div class="form-group">
            <input autocomplete="off" autofocus class="form-control" name="username" placeholder="Username" type="text">
        </div>
        <div class="form-group">
            <input class="form-control" name="password" placeholder="Password" type="password">
        </div>
        <div class="form-group">
            <input class="form-control" name="password-confirm" placeholder="Confirm password" type="password">
        </div>
        <button class="btn btn-primary" type="submit">Register</button>
    </form>
{% endblock %}
"""
