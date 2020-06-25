from application import app
from flask import redirect, url_for
from .helpers import login_required, apology
from werkzeug.exceptions import default_exceptions, HTTPException, \
    InternalServerError
from flask import Blueprint

main = Blueprint("main", __name__)

# Custom filter (this gives an error so I'm commenting it out for now)
# app.jinja_env.filters["usd"] = usd

# Ensure responses aren't cached
@main.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@main.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return redirect(url_for("transactions.sell"))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
