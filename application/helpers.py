from application import app
import requests
import urllib.parse
import sqlite3

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


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = app.config["API_KEY"]
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# set db with sqlite3 instead of cs50's SQL ("Configure CS50 Library to use SQLite database")
def retrieveUsers():
	con = sqlite3.connect("finance.db")
	cur = con.cursor()
	cur.execute("SELECT username, hash FROM users")
	users = cur.fetchall()
	con.close()
	return users

def retrieveUser(username):
	con = sqlite3.connect("finance.db")
	cur = con.cursor()
	cur.execute('SELECT username, hash, id FROM users WHERE username=?', (username,))
	users = cur.fetchall()
	con.close()

	if not users:
		print("no such user")
		return "user does not exist"
	else:
		return users[0]
