# Helpers is being used by models
# Helpers so far handles session, decorators for views and stock API

from application import app
import requests
import urllib.parse
import datetime

from flask import redirect, render_template, request, session, flash
from functools import wraps
from .exceptions import invalidSymbolError, zeroTransactionError


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


def clearSessionExcept(*argv):
    """ Pops any item from session that is not provided as string argument.\n
    csrf_token must be preserved for wtforms validation to work.\n
    _flashes must be preserved for messages to be flashed """
    for key in list(session):
        if key not in argv:
            session.pop(key)


def setSessionStock(keyString, symbol=None, amount=None):
    """ keyString is required: The key for the session entry for stock info.\n
    symbol is optional: if passed in session is repopulated\n
    amount is optional: if passed in amount of stock in question is changed. """
    if keyString not in session:
        # if key not in session, make it exist to be searchable
        session[keyString] = {}
        session[keyString]["amount"] = int(1)
    if symbol:
        oldsymbol = ""
        if "symbol" in session[keyString]:
            oldsymbol = session[keyString]["symbol"]
        try:
            lookupRepopulate(session[keyString], symbol)
            if oldsymbol.lower() != symbol.lower():
                # if it's a different symbol from before, amount is 1
                amount = int(1)
        except invalidSymbolError:
            raise

    # No symbol was passed in. Refresh currect info if exists
    elif "symbol" in session[keyString]:
        symbol = session[keyString]["symbol"]

        try:
            lookupRepopulate(session[keyString], symbol)
        except invalidSymbolError:
            print("Invalid symbol has somehow entered database")
            raise

    if amount is not None:
        if amount > 0:
            session[keyString]["amount"] = int(amount)

        else:
            raise zeroTransactionError
    # Refresh total ( amount is handled )
    if ("price" in session["buystock"]) and ("amount" in session["buystock"]):
        session[keyString]["buytotal"] = float(
            session[keyString]["amount"]) * float(session[keyString]["price"])


def lookupRepopulate(receivingDict, symbol):
    # repopulates keys returned from lookup and leaves the rest be
    dict = lookup(symbol)
    if dict:
        for newKey, newValue in dict.items():
            receivingDict[newKey] = newValue
    else:
        raise invalidSymbolError
