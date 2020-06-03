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
                stock = Stock.get(symbol, amount)
                pricetotal = stock.total

                # Make the transaction: withdraw money, remove amount of owned stocks
                self.cash += pricetotal
                Owned.remove(self, symbol, amount)
                sale = Sales(stock_id=stock.id, amount=amount, unit_price=stock.price, total_price=stock.total)
                self.sales.append(sale)
                db.session.commit()
                flash(u"Sold {} items of {}".format(
                    amount, stock.name), "success")
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
        else:
            stock = Stock.get(symbol, amount)
            if stock:
                pricetotal = stock.total
                if self.cash < pricetotal:
                    # User can't afford
                    flash(f"u broke", "info")
                    return False
                else:
                    # Purchase goes through. Withdraw money, add stock to database,
                    # add stock+amount to user's "Owned", add purchase to user's purchases
                    self.cash -= pricetotal
                    Owned.add(self, stock, amount)
                    purchase = Purchases(stock_id=stock.id, amount=amount, unit_price=stock.price, total_price=pricetotal)
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
        """ Return a list of all transactions sorted by time\n
        name, symbol, amount, total_price, type (sale or purchase) """

        transactionHistory = []
        q = db.session.query

        # Convert queries to dicts, add type and format time and price. Add to list.
        purchaseQuery = q(Purchases.amount, Purchases.total_price, Purchases.time, Stock.symbol, Stock.name).filter(Purchases.user_id == self.id).join(Stock, Stock.id == Purchases.stock_id).group_by(Purchases.id)
        for row in purchaseQuery:
            tempDict = row._asdict()
            tempDict["time"] = tempDict["time"].isoformat()
            tempDict["type"] = "purchase"
            tempDict["total_price"] = "-{:.2f}".format(tempDict["total_price"])
            transactionHistory.append(tempDict)

        saleQuery = q(Sales.amount, Sales.total_price, Sales.time, Stock.symbol, Stock.name).filter(Sales.user_id == self.id).join(Stock, Stock.id == Sales.stock_id).group_by(Sales.id)
        for row in saleQuery:
            tempDict2 = row._asdict()
            tempDict2["time"] = tempDict2["time"].isoformat()
            tempDict2["type"] = "sale"
            tempDict2["total_price"] = "{:+.2f}".format(tempDict2["total_price"])
            transactionHistory.append(tempDict2)

        # Sort the list by time descending and return it
        return sorted(transactionHistory, key=lambda i: i['time'], reverse=True)

class Stock(db.Model):
    __tablename__ = "stocks"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)

    # ORM specific variables
    amount = 0
    price = 0
    total = 0

    @classmethod
    def get(cls, symbol, amount=1):
        """ Returns a stock with fresh info and adds it to database if new. Returns none if invalid symbol """

        stockDict = lookup(symbol)
        if not stockDict:
            return None
        print("stockdict not none: {}".format(stockDict))
        # If we've reached here symbol was valid
        stockSymbol = stockDict["symbol"]
        stockName = stockDict["name"]
        stockPrice = stockDict["price"]

        # If this stock is already in database - use it!
        stock = cls.query.filter_by(symbol=stockSymbol).first()

        # If not already in database - add and then use!
        if not stock:
            stock = cls(symbol=stockSymbol, name=stockName)
            db.session.add(stock)
            db.session.commit()

        stock.price = decimal.Decimal(stockPrice)
        stock.amount = amount if amount >= 1 else 1
        stock.total = stock.amount * stock.price
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
