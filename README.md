**br_system**:
---
- to run locally (with tkinter):
 -- `python br_system.py`
- to run using docker (just cmd app):
1. `export BOOK_NAME={your_book_name}`
2. `docker build -t python-books .`
3. `docker run -e "BOOK_NAME=$BOOK_NAME" python-books`
- after successful run application will print result and return 0 code 
 
