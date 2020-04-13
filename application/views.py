from application import app
from flask import session, request, redirect, render_template, flash, jsonify
from .helpers import login_required, apology, lookup, usd, retrieveUser
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Custom filter (this gives an error so I'm commenting it out for now)
#app.jinja_env.filters["usd"] = usd

# Ensure responses aren't cached
@app.after_request
def after_request(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response


@app.route("/")
@login_required
def index():
	"""Show portfolio of stocks"""
	return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
	"""Buy shares of stock"""
	return apology("TODO")


@app.route("/history")
@login_required
def history():
	"""Show history of transactions"""
	return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
	"""Log user in"""

	# Forget any user_id
	session.clear()

	# User reached route via POST (as by submitting a form via POST)
	if request.method == "POST":

		# Ensure username was submitted
		if not request.form.get("username"):
			return apology("must provide username", 403)

		# Ensure password was submitted
		elif not request.form.get("password"):
			return apology("must provide password", 403)

		# Query database for username
		username = request.form.get("username")
		password = request.form.get("password")

		currentUser = retrieveUser(username)
		currentUsername = currentUser[0]
		currentHash = currentUser[1]
		currentId = currentUser[2]

		# Ensure username exists and password is correct
		if currentUsername == username:
			# Username exists, check password hash:
			if check_password_hash(currentHash, password):
				# Hash was correct - log user in
				print("User can log in")
				session["user_id"] = currentId
			else:
				# User exists but password is incorrect
				print("Incorrect password")
				return apology("invalid password", 403)
		else:
			# User does not exist
			print("user doesn't exist")
			return apology("invalid username", 403)

		# for debugging
		print(session)
		
		"""
		CS50's way of doing it with CS50's SQL library:
		if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
			return apology("invalid username and/or password", 403)

		# Remember which user has logged in
		#session["user_id"] = rows[0]["id"]
		"""

		# Redirect user to home page
		return redirect("/")

	# User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template("login.html")


@app.route("/logout")
def logout():
	"""Log user out"""

	# Forget any user_id
	session.clear()

	# Redirect user to login form
	return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
	"""Get stock quote."""
	return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
	"""Register user"""
	return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
	"""Sell shares of stock"""
	return apology("TODO")


def errorhandler(e):
	"""Handle error"""
	if not isinstance(e, HTTPException):
		e = InternalServerError()
	return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
	app.errorhandler(code)(errorhandler)
