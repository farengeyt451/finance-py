import os
import sqlite3
from datetime import datetime
from tempfile import mkdtemp

from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def dict_factory(cursor, row):
    """Return dictionary instead of default tuple"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db_connection():
    """Create connection to db"""
    connection = sqlite3.connect("finance.db")
    connection.row_factory = dict_factory

    return connection


# Make sure API key is set
if not os.environ.get("IEXCLOUD_API_KEY"):
    raise RuntimeError("IEXCLOUD_API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
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

    if request.method == "POST":
        try:
            conn = get_db_connection()

            user_id = session["user_id"]
            stock_symbol = request.form.get("stock_symbol")
            shares_amount = request.form.get("stock_shares")
            stock_props = lookup(stock_symbol)
            stock_price = stock_props["price"]
            stock_symbol = stock_props["symbol"]
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            if not stock_symbol:
                return apology("required stock symbol")

            if not stock_props:
                return apology("stock symbol does not exit")

            try:
                stock_shares_val = int(shares_amount)

                if stock_shares_val < 0:
                    return apology("shares value must be positive")

            except:
                return apology("shares value must be integer")

            user_cash = conn.execute(
                "SELECT * FROM users WHERE id = ?;", (user_id, )).fetchone()["cash"]

            transaction_value = int(shares_amount) * stock_price

            if transaction_value <= user_cash:

                user_cash_left = user_cash - transaction_value

                conn.execute(
                    "INSERT INTO trans_buy (user_id, symbol, shares_amount, price, transacted) VALUES (?, ?, ?, ?, ?);", (user_id, stock_symbol, shares_amount, stock_price, dt_string))

                conn.execute("UPDATE users SET cash = ? WHERE id = ?;",
                             (user_cash_left, user_id))

                conn.commit()

                flash("Bought")

                return redirect("/")

            else:
                return apology("not enough cash for transaction")

        except:
            return apology("something went wrong")

        finally:
            conn.close()

    return render_template("buy.html")


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
        try:
            conn = get_db_connection()
            username_login = request.form.get("username_login")
            password_login = request.form.get("password_login")

            # Ensure username was submitted
            if not username_login:
                return apology("must provide username", 403)

            # Ensure password was submitted
            elif not password_login:
                return apology("must provide password", 403)

            # Query database for username
            rows = conn.execute("SELECT * FROM users WHERE username = ?;",
                                (username_login, )).fetchall()

            # Ensure username exists and password is correct
            if not rows or not rows[0]["username"] or not check_password_hash(rows[0]["hash"], password_login):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

        except:
            return apology("something went wrong", 500)

        finally:
            conn.close()

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

    if request.method == "POST":
        symbol = request.form.get("stock_quote")

        if not symbol:
            return apology("must provide symbol", 403)

        try:
            response = lookup(symbol)
            return render_template("quoted.html", name=response["name"], symbol=response["symbol"], price=usd(response["price"]))

        except:
            return apology("request failed")

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        try:
            conn = get_db_connection()
            username_form = request.form.get("username")
            username_password = request.form.get("password")
            username_password_confirmation = request.form.get("confirmation")

            username_db = conn.execute("SELECT username FROM users WHERE username = ?;",
                                       (request.form.get("username"), )).fetchone()

            if not username_form:
                return apology("must provide username", 403)

            elif not username_password:
                return apology("must provide password", 403)

            elif username_password != username_password_confirmation:
                return apology("password and password confirmation doesn't match", 403)

            elif username_db:
                return apology("username already exist", 403)

            else:
                password_form = request.form.get("password")

                password_hash = generate_password_hash(
                    password_form, method='pbkdf2:sha256', salt_length=8)

                conn.execute(
                    "INSERT INTO users (username, hash) VALUES(?, ?);", (username_form, password_hash))
                conn.commit()
                return redirect("/")

        except:
            return apology("something went wrong", 500)

        finally:
            conn.close()

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
