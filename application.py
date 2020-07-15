import os
import requests
from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from math import floor

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reg")
def reg():
    return render_template("registration.html")

@app.route("/regac", methods=["POST"])
def regac():
    username = request.form.get("username")
    password = request.form.get("password")
    true_password = (db.execute("select password from account where username = :username",
    {"username": username}).fetchone() or "")
    if (username == "" or password == "" or true_password != ""):
        return render_template("fail.html")
    db.execute("insert into account (username, password) values (:username, :password)",
    {"username": username, "password": password})
    db.commit()
    return render_template("success.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/log")
def log():
    return render_template("login.html")

@app.route("/search", methods=["POST"])
def search():
    username = request.form.get("username")
    password = request.form.get("password")
    true_password = (db.execute("select password from account where username = :username",
    {"username": username}).fetchone() or "")
    if (username == "" or password == "" or true_password == ""):
        return render_template("fail.html")
    elif (password == true_password[0]):
        return render_template("search.html")
    else:
        return render_template("fail.html")

@app.route("/search_result", methods=["POST"])
def search_result():
    type = request.form.get("type")
    info = request.form.get("info")
    if (type == "isbn"):
        books = db.execute("select * from books where isbn like :isbn",
        {"isbn": '%'+info+'%'}).fetchall()
    elif (type == "title"):
        books = db.execute("select * from books where title like :title",
        {"title": '%'+info+'%'}).fetchall()
    elif (type == "author"):
        books = db.execute("select * from books where author like :author",
        {"author": '%'+info+'%'}).fetchall()
    return render_template("search_result.html", books = books)

@app.route("/book_page/<string:isbn>", methods=["POST"])
def book_page(isbn):
    book = db.execute("select * from books where isbn = :isbn",
    {"isbn": isbn}).fetchone()
    ratings_and_comments = db.execute("select rating, comment from comment join books on comment.isbn = books.isbn where comment.isbn = :isbn",
    {"isbn": isbn}).fetchall();

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={
    "key": "CIm8pWjdBp9mXbmMkCodwA", "isbns": isbn})
    data = res.json()
    book_detail = data["books"][0]

    return render_template("book_page.html", book = book, book_detail = book_detail, ratings_and_comments = ratings_and_comments)
    #comment

@app.route("/comment/<string:isbn>", methods=["POST"])
def comment(isbn):
    comment = (request.form.get("comment") or "")
    rating = (int(request.form.get("rating")) or "")
    db.execute("insert into comment (isbn, comment, rating) values (:isbn, :comment, :rating)",
    {"isbn": isbn, "comment": comment, "rating": rating})
    db.commit()
    return render_template("complete.html", isbn = isbn)

@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("select * from books where isbn = :isbn",
    {"isbn": isbn}).fetchone()
    count_and_score = db.execute("select count(*), avg(rating) from comment where isbn = :isbn",
    {"isbn": isbn}).fetchone()

    return jsonify({
        "title": book[1],
        "author": book[2],
        "year": book[3],
        "isbn": book[0],
        "review_count": count_and_score[0],
        "average_score": floor(count_and_score[1])
    })
