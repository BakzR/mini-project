import sqlite3
from pathlib import Path

# The database file is saved in the same folder as this program.
DB_FILE = Path(__file__).with_name("library.db")

LIBRARIAN_NAME = "salman"
LIBRARIAN_PASSWORD = "0000"

STARTING_BOOKS = [
    (101, "Pride and Prejudice", "Jane Austen"),
    (102, "The Hound of the Baskervilles", "Arthur Conan Doyle"),
    (103, "Murder on the Orient Express", "Agatha Christie"),
    (104, "The Time Machine", "H. G. Wells"),
    (105, "The Three Musketeers", "Alexandre Dumas"),
    (106, "The Jungle Book", "Rudyard Kipling"),
]


def connect_db():
    connection = sqlite3.connect(DB_FILE)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    with connect_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                mobile TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0, 1)),
                held_by TEXT,
                FOREIGN KEY (held_by) REFERENCES users(mobile)
            )
        """)

        # Add the sample books only the first time the database is created.
        count = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        if count == 0:
            connection.executemany(
                "INSERT INTO books (id, title, author) VALUES (?, ?, ?)",
                STARTING_BOOKS,
            )


def sign_up():
    print("\n--- Sign up ---")
    name = input("Name: ").strip()
    mobile = input("Mobile number (10 digits): ").strip()
    password = input("Choose a 4-digit password: ").strip()

    if not name:
        print("Name cannot be empty.")
        return
    if len(mobile) != 10 or not mobile.isdigit():
        print("Mobile number must have 10 digits.")
        return
    if len(password) != 4 or not password.isdigit():
        print("Password must have exactly 4 digits.")
        return

    try:
        with connect_db() as connection:
            connection.execute(
                "INSERT INTO users (mobile, name, password) VALUES (?, ?, ?)",
                (mobile, name, password),
            )
        print("Sign up complete. You can log in now.")
    except sqlite3.IntegrityError:
        print("That mobile number is already signed up.")
    except sqlite3.Error as error:
        print("Could not save the account:", error)


def log_in():
    print("\n--- Log in ---")
    mobile = input("Mobile number: ").strip()
    password = input("4-digit password: ").strip()

    with connect_db() as connection:
        user = connection.execute(
            "SELECT name FROM users WHERE mobile = ? AND password = ?",
            (mobile, password),
        ).fetchone()

    if user:
        print("Welcome", user[0])
        return mobile
    print("Login failed. Check your mobile number and password.")
    return None


def show_books():
    print("\n--- Books ---")
    with connect_db() as connection:
        books = connection.execute("""
            SELECT books.id, books.title, books.author, books.available, users.name
            FROM books
            LEFT JOIN users ON books.held_by = users.mobile
            ORDER BY books.id
        """).fetchall()

    if not books:
        print("There are no books in the library.")
        return
    for book_id, title, author, available, holder in books:
        status = "Available" if available else "Borrowed by " + (holder or "a member")
        print(f"{book_id} - {title} by {author} - {status}")


def borrow_book(mobile):
    show_books()
    book_id = input("Book ID to borrow (0 to go back): ").strip()
    if book_id == "0":
        return
    if not book_id.isdigit():
        print("Enter a numeric book ID.")
        return

    with connect_db() as connection:
        cursor = connection.execute(
            "UPDATE books SET available = 0, held_by = ? WHERE id = ? AND available = 1",
            (mobile, int(book_id)),
        )
        if cursor.rowcount:
            title = connection.execute(
                "SELECT title FROM books WHERE id = ?", (int(book_id),)
            ).fetchone()[0]
            print("You borrowed", title)
            return
        exists = connection.execute(
            "SELECT 1 FROM books WHERE id = ?", (int(book_id),)
        ).fetchone()
    print("That book is already borrowed." if exists else "Book ID not found.")


def return_book(mobile):
    book_id = input("Book ID to return (0 to go back): ").strip()
    if book_id == "0":
        return
    if not book_id.isdigit():
        print("Enter a numeric book ID.")
        return

    with connect_db() as connection:
        cursor = connection.execute(
            "UPDATE books SET available = 1, held_by = NULL "
            "WHERE id = ? AND held_by = ?",
            (int(book_id), mobile),
        )
        if cursor.rowcount:
            print("You returned the book.")
            return
        book = connection.execute(
            "SELECT available, held_by FROM books WHERE id = ?", (int(book_id),)
        ).fetchone()

    if book is None:
        print("Book ID not found.")
    elif book[0]:
        print("That book is already in the library.")
    else:
        print("You cannot return a book borrowed by another member.")


def reader_menu(mobile):
    while True:
        print("\n=== Welcome to World of Reading ===")
        print("1. Borrow books")
        print("2. Return books")
        print("3. Show books")
        print("0. Log out")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            borrow_book(mobile)
        elif choice == "2":
            return_book(mobile)
        elif choice == "3":
            show_books()
        elif choice == "0":
            print("Please visit again.")
            return
        else:
            print("Choose 1, 2, 3, or 0.")


def librarian_menu():
    while True:
        print("\n--- Librarian menu ---")
        print("1. Add a book")
        print("2. Remove a book")
        print("3. Show books")
        print("0. Log out")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            title = input("Book title: ").strip()
            author = input("Author: ").strip()
            if not title or not author:
                print("Enter both a title and an author.")
                continue

            with connect_db() as connection:
                row = connection.execute(
                    "SELECT MIN(id) FROM books WHERE id BETWEEN 101 AND 999 "
                    "AND id NOT IN (SELECT id FROM books)"
                ).fetchone()
                # MIN over no rows is NULL; find the first unused three-digit ID.
                new_id = row[0]
                if new_id is None:
                    used_ids = {r[0] for r in connection.execute(
                        "SELECT id FROM books WHERE id BETWEEN 101 AND 999"
                    )}
                    new_id = next((i for i in range(101, 1000) if i not in used_ids), None)

                if new_id is None:
                    print("No three-digit book IDs are available.")
                else:
                    connection.execute(
                        "INSERT INTO books (id, title, author) VALUES (?, ?, ?)",
                        (new_id, title, author),
                    )
                    print("Book added with ID", new_id)
        elif choice == "2":
            book_id = input("Book ID to remove: ").strip()
            if not book_id.isdigit():
                print("Enter a numeric book ID.")
                continue
            with connect_db() as connection:
                cursor = connection.execute(
                    "DELETE FROM books WHERE id = ? AND available = 1", (int(book_id),)
                )
            if cursor.rowcount:
                print("Book removed.")
            else:
                print("Book not found or currently borrowed; return it before removing.")
        elif choice == "3":
            show_books()
        elif choice == "0":
            print("Librarian logged out.")
            return
        else:
            print("Choose an option from the list.")


def main():
    create_tables()

    while True:
        print("\n=== World of Reading ===")
        print("1. Sign up")
        print("2. Log in")
        print("3. Librarian log in")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            sign_up()
        elif choice == "2":
            mobile = log_in()
            if mobile:
                reader_menu(mobile)
        elif choice == "3":
            name = input("Librarian name: ").strip()
            password = input("Librarian 4-digit password: ").strip()
            if name == LIBRARIAN_NAME and password == LIBRARIAN_PASSWORD:
                print("Librarian login successful.")
                librarian_menu()
            else:
                print("Librarian name or password is incorrect.")
        elif choice == "0":
            print("Goodbye!")
            return
        else:
            print("Choose an option from the list.")


if __name__ == "__main__":
    main()
