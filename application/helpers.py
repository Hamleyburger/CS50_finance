# Helpers is being used by models and dbhelpers and must not import models or
# dbhelpers (because it will create circular import)
# Helpers so far handles session, decorators for views and stock API

from application import app
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session, flash
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
    print("urllib.parse= {}".format(urllib.parse.quote_plus(symbol)))
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


def clearSessionKeepFlash():
    # Forget any user_id, but maintain message flash if present
    if session.get("_flashes"):
        flashes = session.get("_flashes")
        session.clear()
        session["_flashes"] = flashes
    else:
        session.clear()


def setSessionStock(keyString, symbol=None, amount=None):
    """
    instantiate stock info in session if none
    refresh stock info if symbol is valid
    refresh stock info and maintain amount if same
    refresh stock info and reset amount if new
    "keyString" is the session key
    """

    if keyString not in session:
        # if key not in session, make it exist to be searchable
        session[keyString] = {}
        session[keyString]["amount"] = 1
    if symbol:
        if lookup(symbol):
            if "symbol" in session["buystock"]:
                if session["buystock"]["symbol"].lower() != symbol.lower():
                    # if it's a different symbol from before, amount is 1
                    amount = 1
            else:
                amount = 1

        # try to refresh session with new data from lookup
        lookupRepopulate(session[keyString], symbol)
    # No symbol was passed in. Refresh currect info if exists
    elif "symbol" in session[keyString]:
        symbol = session[keyString]["symbol"]
        lookupRepopulate(session[keyString], symbol)

    if amount:
        session[keyString]["amount"] = amount


def lookupRepopulate(receivingDict, symbol):
    # repopulates keys returned from lookup and leaves the rest be
    if lookup(symbol):
        for newKey, newValue in lookup(symbol).items():
            receivingDict[newKey] = newValue
    else:
        flash(u"Could not find stock symbol in database", "danger")
