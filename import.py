import os,csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# setup db connection
dburl = 'postgres://fgzgiqkqolatya:112edd8b5a4c58719ab809e153ab78bbb8cde9761011e475402ad146e1a4f138@ec2-174-129-18-42.compute-1.amazonaws.com:5432/d30sblqvqmohhf'
engine = create_engine(dburl)
db = scoped_session(sessionmaker(bind=engine))

# get file handler and reader
f = open("books.csv")
reader = csv.reader(f)

# loop over file contents line by line
for isbn,title,author,year in reader:

    if year == 'year':
        continue

    print("processing", isbn)

    db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn, :title, :author, :year)",
                  {"isbn": isbn, "title": title, "author": author , "year": year})

# commit db changes
db.commit()

# release file handle
f.close()


print ("All done")