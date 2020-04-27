from application import db
import datetime
from werkzeug.security import generate_password_hash
from .helpers import lookup
import decimal


"""
CREATE TABLE 'users'
('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
'username' TEXT NOT NULL,
'hash' TEXT NOT NULL,
'cash' NUMERIC NOT NULL DEFAULT 10000.00 )
"""


class User(db.Model):

    # Table
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    hash = db.Column(db.String(), nullable=False)
    # server_default sets actual default value in database. If ONLY ORM is
    # used to communicate with the db, setting default is enough.
    # server_default does not take a plain number, sp use db.text() to set it
    cash = db.Column(db.Numeric, nullable=False,
                     server_default=db.text('10000.00'))

    # Relationships
    sales = db.relationship("Sales", backref="user", lazy=True)
    purchases = db.relationship("Purchases", backref="user", lazy=True)
    owned = db.relationship("Stock", secondary="owned", backref=db.backref("users", lazy=True))

    # Methods for class in general
    def create(username, password):
        # Insert user and hashed password into database
        hash = generate_password_hash(password)
        user = User(username=username,
                    hash=hash)
        db.session.add(user)
        db.session.commit()

    def get(username):
        # This method returns user if exists, otherwise None
        user = User.query.filter_by(username=username).first()
        if not user:
            print("user.get: query returned None")
            return None
        else:
            return user

    # Methods for instantiated objects
    def buy(self, symbol, amount):
        # Buy is a bool that returns true if success and false
        # if user doesn't have enough money
        if lookup(symbol):
            stockDict = lookup(symbol)
            pricetotal = float(stockDict["price"]) * float(amount)
            cash = float(self.cash)
            if cash < pricetotal:
                print("User has {:.2f} and needs {:.2f}. This sucks.".format(cash, pricetotal))
                return False
            else:
                print("User has {:.2f} and buys stocks for {:.2f}".format(cash, pricetotal))
                self.cash -= decimal.Decimal(pricetotal)
                Owned.add(self, symbol, amount)
                db.session.commit()
                # Make a methid in Owned (instantiated?) that adds amount owned if not exists.
                # If it exists alter amount.
                # Also a method for subtracting if exists will be needed.
                return True
        else:
            print("Attempted to buy stock of unvalid symbol")
            return False


class Stock(db.Model):
    __tablename__ = "stocks"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)

    # Adds a stock to database if it doesn't already exists.
    # Because in that way only stocks relevant to the app will be added
    # to database.
    def get(symbol):
        stockDict = {}
        if lookup(symbol):
            stockDict = lookup(symbol)
        else:
            return None
        # If we've reached here stockDict has content
        stockSymbol = stockDict["symbol"]
        stockName = stockDict["name"]

        # If this stock is already in database - use it!
        stock = Stock.query.filter_by(symbol=stockSymbol).first()

        # If not already in database - add and then use!
        if not stock:
            stock = Stock(symbol=stockSymbol, name=stockName)
            db.session.add(stock)
            db.session.commit()
        
        # Return whatever stock ended up being set to
        return stock


# Associational table between User and Stock
class Owned(db.Model):
    __tablename__ = "owned"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey(
        'stocks.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def add(user, symbol, amount):
        stock = Stock.get(symbol)
        amount = int(amount)
        owned = Owned.query.filter_by(user_id=user.id, stock_id=stock.id).first()
        if owned:
            print("user already owns some amount of this")
            owned.amount += amount
        else:
            print("User bought this for the first time.")
            owned = Owned(user_id=user.id, stock_id=stock.id, amount=amount)
            db.session.add(owned)
        db.session.commit()


class Sales(db.Model):
    __tablename__ = "sales"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey(
        'stocks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric, nullable=False)
    total_price = db.Column(db.Numeric, nullable=False)
    time = db.Column(db.DateTime, nullable=False,
                     default=datetime.datetime.utcnow().isoformat())


class Purchases(db.Model):
    __tablename__ = "purchases"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey(
        'stocks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric, nullable=False)
    total_price = db.Column(db.Numeric, nullable=False)
    time = db.Column(db.DateTime, nullable=False,
                     default=datetime.datetime.utcnow().isoformat())
