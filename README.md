# Project 1

Web Programming with Python and JavaScript

Project Author: Isaac Newton Kissiedu

This project is a Flask web app for Book Reviews.

The project relies on HTML, CSS,Bootstrap Framework, Python, Flask and PostgreSQL for storing permanent data in a database.

FILES IN THE PROJECT

1. application.py: This is the main python module for controlling the entire application. It defines the application by creating routes and functions for handling requests such as Login, Register,Search, Reivew a book etc.

2. books.csv: This is a flat file that contains a list of books to be imported into the postgresql database

3. import.py: This is a pyton module that imports the list of books found in the books.csv into the postgresql database. It first create a connection to the database, reads the file and imports it using the Python SQLAlchemy API.

4. README.md: This file is for telling contributors about the content of this project and how to use it

5. requirements.txt : This file contains all the Pyton dependencies to be installed before running the application

6. templates: This is a folder that contains all the html files. By convension, Flask will load html files from here

7. static: This is a folder that contains all the site javascript and stylesheets

8. flask_session: This is a folder that is used by Flask for session storage on disk