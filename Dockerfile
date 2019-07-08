FROM python:3

ADD br_system.py br_system.py
ADD BX-Book-Ratings.csv BX-Book-Ratings.csv
ADD BX-Books.csv BX-Books.csv
ADD BX-Users.csv BX-Users.csv
ADD requirements.txt requirements.txt


ENV BOOK_NAME "The Green Mile: Night Journey (Green Mile Series)"
RUN pip install -r requirements.txt



CMD [ "python", "./br_system.py" ]

# docker rmi $(docker images -q)
# docker build -t python-books .
# docker run -e "BOOK_NAME=$BOOK_NAME" python-books
# try with this `The Green Mile: Night Journey (Green Mile Series)`




