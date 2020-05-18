from application import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .helpers import lookup
import decimal
from flask import flash
from .exceptions import userNotFoundError, invaldPasswordError


class User(db.Model):
    """Has everything that the user has and does"""
    # Table
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    hash = db.Column(db.String(), nullable=False)
    # server_default sets actual default value in database. If ONLY ORM is
    # used to communicate with the db, setting default is enough.
    # server_default does not take a plain number, so use db.text() to set it
    cash = db.Column(db.Numeric, nullable=False,
                     server_default=db.text('10000.00'))

    # Relationships
    sales = db.relationship("Sales", backref="user", lazy=True)
    purchases = db.relationship("Purchases", backref="user", lazy=True)
    owned = db.relationship("Stock", secondary="owned",
                            backref=db.backref("users", lazy=True))

    # Methods for class in general
    @classmethod
    def create(cls, username, password):
        """ Inserts user and hash to database.\n
        Assumes that username and passwords are valid!!
        returns the new user"""
        # Insert user and hashed password into database
        try:
            hash = generate_password_hash(password)
            user = cls(username=username,
                    hash=hash)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            print(e)
            raise

    @classmethod
    def get(cls, username):
        """This method returns user if exists, otherwise None"""
        user = cls.query.filter_by(username=username).first()
        return user

    @classmethod
    def verify(cls, username, password):
        """ Sets username, user ID and cash in session if username and passwords match\n
        Returns user"""
        # Ensure username exists and password is correct
        user = cls.get(username)
        if user:
            # Username exists, check password hash:
            if check_password_hash(user.hash, password):
                # Hash was correct - log user in
                return user
            else:
                raise invaldPasswordError("Incorrect password")
        else:
            raise userNotFoundError(f'User "{username}" not found')

    # Methods for instantiated objects
    def amountOwned(self, symbol):
        """Expects valid stock symbol.\n
        Returns the amount of given stock (from symbol) owned or None\n
        """
        symbol = symbol.upper()
        ownedStock = Owned.query.filter_by(user_id=self.id).join(
            Stock).filter_by(symbol=symbol).first()
        if ownedStock:
            return ownedStock.amount
        else:
            return 0

    def sell(self, symbol, amount):
        """Returns true if success. """
        # Check that amount >0
        if int(amount) > 0:
            # Check that user owns this stock and enough
            amountOwned = self.amountOwned(symbol)
            if amountOwned >= amount:
                # User owns enouh of this stock. Calculate value
                stockDict = lookup(symbol)
                pricetotal = decimal.Decimal(
                    stockDict["price"]) * decimal.Decimal(amount)

                # Make the transaction: withdraw money, remove amount of owned stocks
                self.cash += pricetotal
                Owned.remove(self, symbol, amount)
                flash(u"Sold {} items of {}".format(
                    amount, stockDict["name"]), "success")
                return True
            elif amountOwned == 0:
                flash(u"You don't have any of this stock", "danger")
            else:
                flash(u"You don't own enough of this stock", "danger")
        else:
            flash(u"You can't sell 0 stocks", "danger")
        return False

    def buy(self, symbol, amount):
        # Buy is a bool that returns true if success and false
        # if user doesn't have enough money
        if int(amount) < 1:
            # User tried to buy less than one
            return False
        elif lookup(symbol):
            stockDict = lookup(symbol)
            pricetotal = decimal.Decimal(
                stockDict["price"]) * decimal.Decimal(amount)
            if self.cash < pricetotal:
                # User can't afford
                return False
            else:
                # Purchase goes through. Withdraw money, add stock to database,
                # add stock+amount to user's "Owned", add purchase to user's purchases
                self.cash -= pricetotal
                stock = Stock.get(symbol)
                Owned.add(self, stock, amount)
                purchase = Purchases(stock_id=stock.id, amount=amount, unit_price=decimal.Decimal(
                    stockDict["price"]), total_price=pricetotal)
                self.purchases.append(purchase)
                db.session.commit()
                # Make a methid in Owned (instantiated?) that adds amount owned if not exists.
                # If it exists alter amount.
                # Also a method for subtracting if exists will be needed.
                return True
        else:
            print("Attempted to buy stock of invalid symbol")
            return False


class Stock(db.Model):
    __tablename__ = "stocks"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)

    # Checks with a stock symbol if the stock exists
    # If it exists in API return it, else return None
    # If it did not exist in database Stocks table, add it.
    @classmethod
    def get(cls, symbol):
        stockDict = {}
        if lookup(symbol):
            stockDict = lookup(symbol)
        else:
            return None
        # If we've reached here stockDict has content
        stockSymbol = stockDict["symbol"]
        stockName = stockDict["name"]

        # If this stock is already in database - use it!
        stock = cls.query.filter_by(symbol=stockSymbol).first()

        # If not already in database - add and then use!
        if not stock:
            stock = cls(symbol=stockSymbol, name=stockName)
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

    @classmethod
    def add(cls, user, stock, amount):
        amount = int(amount)
        owned = cls.query.filter_by(
            user_id=user.id, stock_id=stock.id).first()
        if owned:
            print("user already owns some amount of this")
            owned.amount += amount
        else:
            print("User bought this for the first time.")
            owned = cls(user_id=user.id, stock_id=stock.id, amount=amount)
            db.session.add(owned)
        db.session.commit()

    @classmethod
    def remove(cls, user, symbol, amount):
        symbol = symbol.upper()
        stock = Stock.get(symbol)
        owned = cls.query.filter_by(user_id=user.id, stock_id=stock.id).first()
        if owned:
            owned.amount -= amount
            print("{} now owns {} {}".format(
                user.username, owned.amount, stock.name))
            if owned.amount == 0:
                print("attempting to remove owned")
                print(owned)
                db.session.delete(owned)
        else:
            print("User does not own this.")
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
                     default=datetime.datetime.utcnow())
    # Remember to return time in .isoformat() for displaying in the browser by
    # formattingwith moment.js
