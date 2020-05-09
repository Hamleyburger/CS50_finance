# dbhelpers helps to handle models and might as well be in models.py. Do not import to helpers.py

from application import db
from .helpers import lookup
from .models import User, Stock, Owned
from flask import session
# for handling passwords (with database)
from werkzeug.security import check_password_hash


def userVerified(username, password):
    """ Sets username, user ID and cash in session if username and passwords match """
    # Ensure username exists and password is correct
    if User.get(username):
        user = User.get(username)

        # Username exists, check password hash:
        if check_password_hash(user.hash, password):
            # Hash was correct - log user in
            print("userVerified: hash and password match!")
            session["user_id"] = user.id
            session["username"] = user.username
            session["cash"] = user.cash
            return True
        else:
            # User exists but password is incorrect
            print("userVerified: hash and password didn't match")
            return False
    else:
        # User does not exist
        print("userVerified: User.get returned None")
        return False

"""
# This function only exists for testing purposes and will be removed
def dataHandle():
    user = User.query.filter_by(username="admin").first()
    if Stock.get("goog"):
        stock = Stock.get("goog")
    else:
        return
    #owned = Owned.query.filter_by(user_id=user.id, stock_id=stock.id).first()
    owned = Owned(user_id=user.id, stock_id=stock.id, amount=1)
    db.session.add(owned)
    owned.amount += 3
    db.session.commit()
    print(user.username)
    print(stock.name)
    for stock in user.owned:
        print(stock.name)
    
    for user in stock.users:
        print(user.username)
"""
