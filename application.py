import os, requests, json, hashlib

from flask import Flask, session, render_template, request, flash, redirect, url_for, Response
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://fgzgiqkqolatya:112edd8b5a4c58719ab809e153ab78bbb8cde9761011e475402ad146e1a4f138@ec2-174-129-18-42.compute-1.amazonaws.com:5432/d30sblqvqmohhf")
db = scoped_session(sessionmaker(bind=engine))
salt = "cs50prj1"

@app.route("/", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')

    # Start processing
    username = request.form.get("username")
    password = request.form.get("password")
    repeatpassword = request.form.get("repeatpassword")

    errors = []

    # Validation
    if username == "" or username is None:
        errors.append("Username is required")

    if password == "" or password is None:
        errors.append("Password is required")

    if repeatpassword == "" or password is None:
        errors.append("Repeat password is required")
    elif repeatpassword != password:
        errors.append("Passwords do not match")

    # check that the user does not already exist
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
        errors.append("Username already exist")

    # go back to form if there were validation errors
    if len(errors) > 0:
        return render_template('register.html', errors=errors)


    # Continue processing
    db_password = password + salt
    h = hashlib.md5(db_password.encode())
    hash_password = h.hexdigest()

    db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",
                  {"username": username, "password": hash_password})
    db.commit()

    # Inform registration successful
    flash("Registration successful!")

    return redirect( url_for('login') )
    
    

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')

    # Process post
    username = request.form.get("username")
    password = request.form.get("password")
    db_password = password + salt
    h = hashlib.md5(db_password.encode())
    hash_password = h.hexdigest()

    errors = []

    user = db.execute("SELECT * FROM users WHERE username = :username and password= :password",
                    {"username": username, "password": hash_password}).first()

    if user is None:
        errors.append("Invalid username or password")
        return render_template('login.html',errors=errors)

    else:
        # Found user
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect( url_for('search') )



@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route("/search", methods = ["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template('search.html')

    # Start processing
    searchby = request.form.get("searchby")
    serachvalue = request.form.get("searchvalue")

    errors = []

    # Validation
    if searchby == "" or searchby is None:
        errors.append("Search By is required")

    if serachvalue == "" or serachvalue is None:
        errors.append("Search Value is required")

    # go back to form if there were validation errors
    if len(errors) > 0:
        return render_template('search.html', errors=errors)


    # Continue processing
    result = None
    if searchby == "isbn":
       result = db.execute("SELECT * FROM books WHERE isbn ilike :searchvalue", {"searchvalue": '%' + serachvalue + '%'})
    elif searchby == "title":
       result = db.execute("SELECT * FROM books WHERE title ilike :searchvalue", {"searchvalue": '%' + serachvalue + '%'})
    else:
       result = db.execute("SELECT * FROM books WHERE author ilike :searchvalue", {"searchvalue": '%' + serachvalue + '%'})

    books = result.fetchall()

    return render_template('search.html', books=books)


@app.route("/book/<string:isbn>", methods = ["GET", "POST"])
def book(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn }).first()
    reviews = db.execute("SELECT r.comment,r.rate,u.username FROM reviews as r \
                         LEFT JOIN users as u ON r.user_id = u.id \
                         WHERE book_id = :book_id", {"book_id": book[0] }).fetchall()

    reviews_all = []
    for review in reviews:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", 
                        params={"key": "BY3hwvsjkQmMMlf7yYA", "isbns": isbn})

        stats_dict = res.json()['books'][0]

        ratings_count = stats_dict['ratings_count']
        avg_rating = stats_dict['average_rating']

        new_review = list(review)
        new_review.append(ratings_count)
        new_review.append(avg_rating)

        reviews_all.append(new_review)
        
        


    if request.method == "GET":
        return render_template('book.html', book = book, reviews = reviews_all)

    
    # Start processing
    rate    = request.form.get("rate")
    comment = request.form.get("comment")
    user_id = session.get('user_id', None)
    book_id = book[0]

    errors = []

    # Validation
    if rate == "" or rate is None:
        errors.append("Rate is required")

    if comment == "" or comment is None:
        errors.append("Comment is required")

    if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id=:book_id",
                        {"user_id": user_id, "book_id":book_id}).rowcount > 0:
        errors.append("User has already reviewed this book")

    # go back to form if there were validation errors
    if len(errors) > 0:
        return render_template('book.html', book=book, reviews= reviews, errors=errors)


    # Continue processing
    db.execute("INSERT INTO reviews (comment,rate,user_id,book_id) VALUES (:comment, :rate, :user_id, :book_id)",
                  {"comment": comment, "rate": rate, "user_id": user_id, "book_id": book_id})
    db.commit()

    # Inform success
    flash("Review added successfully!")

    return redirect( url_for('book', isbn = isbn) )



@app.route("/api/<isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn }).first()
    book_stats = db.execute("SELECT coalesce(count(id),0) as review_count, coalesce(avg(rate),0) as average_score \
                            FROM reviews WHERE book_id = :book_id", {"book_id": book[0]}).first()

    result = {'title': book[2], 
             'author': book[3],
             'year'  : book[4],
             'isbn'  : book[1],
             'review_count': book_stats[0],
             'average_score': float(book_stats[1])}

    return Response(json.dumps(result),  mimetype='application/json')