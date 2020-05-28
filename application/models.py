from application import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .helpers import lookup
import decimal
from flask import flash
from .exceptions import userNotFoundError, invaldPasswordError
from collections import namedtuple
from sqlalchemy.sql import func


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
        """ Sets username, user ID and cash in session if username and\n
        passwords match. Returns user """
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
    def ownedStocks(self):
        """
        Gets user's owned stocks and returns list of named tuples \n
        with name, symbol, amount and current price pr. unit
        """
        print("Owned called")
        ownedStocks = db.session.query(Stock.name, Stock.symbol, Owned.amount, func.sum(Purchases.total_price).label("total_spent")).join(Owned).join(Purchases).filter(Owned.user_id == self.id).group_by(Purchases.stock_id).all()

        stocksWithPrices = []
        # Named tuple returns a nice, readable object-like tuple for easy access
        StockTuple = namedtuple("stockTuple", ["name", "symbol", "amount", "price", "total_spent"])

        for stock in ownedStocks:
            price = lookup(stock.symbol)["price"]
            stockTuple = StockTuple(stock.name, stock.symbol, stock.amount, price, stock.total_spent)
            stocksWithPrices.append(stockTuple)

        return stocksWithPrices

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
        """ Returns true if success. """
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
                sale = Sales(stock_id=Stock.get(symbol).id, amount=amount, unit_price=decimal.Decimal(stockDict["price"]), total_price=pricetotal)
                self.sales.append(sale)
                db.session.commit()
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

    def transactions(self):
        q = db.session.query
        q1 = q(Purchases, Stock.symbol).filter(Purchases.user_id == self.id).join(Stock)
        q2 = q(Sales, Stock.symbol).filter(Sales.user_id == self.id).join(Stock)

        q3 = q1.union(q2)

        for row in q3:
            print(f"{row.symbol} {row.Purchases.amount} {row.Purchases.total_price} {row.Purchases.time.isoformat()}")

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
    def add(cls, user, stock, amount, commit=False):
        """ adds stock to user's index. Don't forget to commit or set commit to True! """
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
        if commit:
            db.session.commit()

    @classmethod
    def remove(cls, user, symbol, amount, commit=False):
        """ Removes stock from user's owned list. Either commit afterwards or set commit to True """
        symbol = symbol.upper()
        stock = Stock.get(symbol)
        owned = cls.query.filter_by(user_id=user.id, stock_id=stock.id).first()
        if owned:
            owned.amount -= amount
            print("{} now owns {} {}".format(
                user.username, owned.amount, stock.name))
            if owned.amount == 0:
                db.session.delete(owned)
        else:
            print("User does not own this.")
        if commit:
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
                     default=datetime.datetime.utcnow())


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
