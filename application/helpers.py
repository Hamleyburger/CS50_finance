from application import app
import requests
import urllib.parse
import datetime

# for handing database
import sqlite3
# for handling passwords (with database)
from werkzeug.security import check_password_hash, generate_password_hash

from flask import redirect, render_template, request, session
from functools import wraps

# Until I figure out how to use sqlalchemy I need this dbPath to set path to db
dbPath = app.config["DB_PATH"]

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
			"symbol": quote["symbol"],
			"isotime": datetime.datetime.utcnow().isoformat()
		}

	except (KeyError, TypeError, ValueError):
		return None


def usd(value):
	"""Format value as USD."""
	return f"${value:,.2f}"

# set db with sqlite3 instead of cs50's SQL ("Configure CS50 Library to use SQLite database")

# Retrieve a list of all users
def retrieveUsers():
	con = sqlite3.connect(dbPath)
	cur = con.cursor()
	cur.execute("SELECT username, hash FROM users")
	users = cur.fetchall()
	con.close()
	return users

def retrieveUser(username):
	con = sqlite3.connect(dbPath)
	cur = con.cursor()
	cur.execute('SELECT username, hash, id FROM users WHERE username=?', (username,))
	users = cur.fetchall()
	con.close()

	if not users:
		print("no such user")
		return None
	else:
		return users[0]

def userVerified(username, password):
	# Ensure username exists and password is correct
	if retrieveUser(username):
		currentUser = retrieveUser(username)
		currentHash = currentUser[1]
		currentId = currentUser[2]

		# Username exists, check password hash:
		if check_password_hash(currentHash, password):
			# Hash was correct - log user in
			print("User can log in")
			session["user_id"] = currentId
			return True
		else:
			# User exists but password is incorrect
			print("Incorrect password")
			return False
	else:
		# User does not exist
		print("user doesn't exist")
		return False



def createUser(username, password):
	# Insert user and hashed password into database
	#db.execute("INSERT INTO users (username,hash) VALUES (?, ?)", form("username"), generate_password_hash(form("password")))
	con = sqlite3.connect(dbPath)
	cur = con.cursor()
	cur.execute("INSERT INTO users (username,hash) VALUES (?, ?)", (username, generate_password_hash(password)))
	#users = cur.fetchall()
	con.commit()
	con.close()

def clearSessionKeepFlash():
	# Forget any user_id, but maintain message flash if present
	if session.get("_flashes"):
		flashes = session.get("_flashes")
		session.clear()
		session["_flashes"] = flashes
	else:
		session.clear()