from flask import session, request, redirect, render_template, flash, jsonify
from .helpers import clearSessionExcept
from application.models import User
from .forms import RegistrationForm, LoginForm
from flask import Blueprint

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
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


@users.route("/login", methods=["GET", "POST"])
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


@users.route("/ajax", methods=["POST"])
# Route just for trying out AJAX - checks if user exists for quick front end feedback
def ajax():
    username = request.form["username"]
    exists = False

    if User.get(username):
        exists = True
    else:
        exists = False

    return jsonify({"exists": exists})


@users.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
