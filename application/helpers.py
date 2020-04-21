from application import app, db
import requests
import urllib.parse
import datetime
from .models import User

# for handling passwords (with database)
from werkzeug.security import check_password_hash


from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Changed lookup to also return UTC time stamp in isoformat: ["isotime"]
def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = app.config["API_KEY"]
        response = requests.get(
            f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:

        quote = response.json()

        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"],
            "isotime": datetime.datetime.utcnow().isoformat()
        }

    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def getUser(username):

    user = User.query.filter_by(username=username).first()

    if not user:
        print("getUser: query returned None")
        return None
    else:
        return user


def userVerified(username, password):
    # Ensure username exists and password is correct
    if getUser(username):
        user = getUser(username)

        # Username exists, check password hash:
        if check_password_hash(user.hash, password):
            # Hash was correct - log user in
            print("userVerified: hash and password match!")
            session["user_id"] = user.id
            return True
        else:
            # User exists but password is incorrect
            print("userVerified: hash and password didn't match")
            return False
    else:
        # User does not exist
        print("userVerified: getUser returned None")
        return False


def createUser(username, password):
    User.create(username, password)


def clearSessionKeepFlash():
    # Forget any user_id, but maintain message flash if present
    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
        session.clear()
