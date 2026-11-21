World of Reading - Library Management System

About

This is a small Python library program. Members can create an account, log in, borrow books, and return books. The librarian can add books, remove books, and see whether a book is available or who has borrowed it.

The program saves its information in an SQLite database. You do not need to install SQLite separately; Python includes the `sqlite3` module.

Files

* `library_sqlite.py` is the program.
*`library.db` is the database. The program creates it in the same folder when it starts.

Member instructions

1. Choose `1. Sign up`.
2. Enter your name, a 10-digit mobile number, and a 4-digit password.
3. Return to the main menu and choose `2. Log in`.
4. Enter your mobile number and password.
5. In the member menu, choose an option:
   - `1` to borrow a book. Enter its book ID.
   - `2` to return a book you borrowed. Enter its book ID.
   - `3` to see the book list and borrowing status.
   - `0` to log out.


 Librarian instructions

1. At the main menu, choose `3. Librarian log in`.
2. Enter the current librarian details:

   - Name: `salman`
   - Password: `0000`

3. Choose an option:
   - `1` to add a book. Enter its title and author. The program chooses an unused three-digit ID.
   - `2` to remove a book. Borrowed books must be returned before they can be removed.
   - `3` to see books and who is holding borrowed books.
   - `0` to log out.


