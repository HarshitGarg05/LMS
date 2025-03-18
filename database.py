import json
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.users_file = "users.json"
        self.books_file = "books.json"
        self.borrow_log_file = "borrow_log.json"
        
        self.users = self.load_users()
        self.books = self.load_books()
        self.borrow_log = self.load_borrow_log()

    # ---------- USER MANAGEMENT ----------
    
    def load_users(self):
        """Load users from JSON file into a hash table (dictionary)."""
        try:
            with open(self.users_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_users(self):
        """Save the hash table to a JSON file for persistence."""
        with open(self.users_file, "w") as file:
            json.dump(self.users, file, indent=4)

    def register_user(self, user_id, name, password, user_type):
        """Register a new user (student or librarian)."""
        if user_id in self.users:
            return False  # User already exists

        self.users[user_id] = {
            "name": name,
            "password": password,
            "user_type": user_type
        }
        self.save_users()
        return True

    def authenticate_user(self, user_id, password):
        """Check if a user exists and the password is correct."""
        user = self.users.get(user_id)
        if user and user["password"] == password:
            return user
        return None

    # ---------- BOOK MANAGEMENT ----------
    
    def load_books(self):
        """Load books from JSON file into a hash table (dictionary) and ensure copies are integers."""
        try:
            with open(self.books_file, "r") as file:
                books = json.load(file)
                for book_id in books:
                    books[book_id]["copies"] = int(books[book_id]["copies"])
                return books
        except FileNotFoundError:
            return {}

    def save_books(self):
        """Save the books hash table to a JSON file for persistence."""
        with open(self.books_file, "w") as file:
            json.dump(self.books, file, indent=4)

    def add_book(self, book_id, title, author, copies):
        """Add a new book to the database."""
        if book_id in self.books:
            return "Book ID already exists!"

        self.books[book_id] = {
            "title": title,
            "author": author,
            "copies": int(copies)  # Ensure copies is an integer
        }
        self.save_books()
        return "Book added successfully!"

    def edit_book(self, book_id, title, author, copies):
        """Edit an existing book."""
        if book_id not in self.books:
            return "Book not found!"

        self.books[book_id] = {
            "title": title,
            "author": author,
            "copies": int(copies)  # Ensure copies is an integer
        }
        self.save_books()
        return "Book updated successfully!"

    def delete_book(self, book_id):
        """Delete a book from the database."""
        if book_id in self.books:
            del self.books[book_id]
            self.save_books()
            return "Book deleted successfully!"
        return "Book not found!"

    def get_all_books(self):
        """Return all books in the database."""
        return self.books  # Ensure this returns a dictionary of books


    # ---------- BORROW & RETURN SYSTEM ----------




    def load_borrow_log(self):
        """Load borrow records from JSON and handle empty or corrupt data."""
        try:
            with open(self.borrow_log_file, "r") as file:
                data = file.read().strip()  # Remove unwanted spaces
                if not data:  # If file is empty
                    return []
                return json.loads(data)  # Parse JSON
        except (FileNotFoundError, json.JSONDecodeError):  # Catch corrupt JSON
            return []  # Return an empty list if error occurs


    def save_borrow_log(self, borrow_log):
        """Save borrow records to JSON."""
        with open(self.borrow_log_file, "w") as file:
            json.dump(borrow_log, file, indent=4)

    def borrow_book(self, student_id, book_id):
        """Allow a student to borrow a book and track due date."""
        if book_id not in self.books:
            return "Book not found!"

        if int(self.books[book_id]["copies"]) > 0:
            self.books[book_id]["copies"] -= 1
            self.save_books()

            # Set borrow date and due date in YYYY-MM-DD format
            borrow_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")  # Ensure correct format

            # Save the transaction in a borrow log
            borrow_log = self.load_borrow_log()

            borrow_log.append({
                "student_id": student_id,
                "book_id": book_id,
                "borrow_date": borrow_date,
                "due_date": due_date  # Stored as YYYY-MM-DD
            })

            self.save_borrow_log(borrow_log)

            return f"Book borrowed successfully! Due Date: {due_date}"
        
        return "Book is not available!"
    
    def return_book(self, student_id, book_id):
        """Allow a student to return a borrowed book and update copies correctly."""
        borrow_log = self.load_borrow_log()

        for record in borrow_log:
            if record["student_id"] == student_id and record["book_id"] == book_id:
                due_date = record.get("due_date", None)  # Ensure due_date exists
                return_date = datetime.now().strftime("%Y-%m-%d")

                # Calculate fine (₹5 per day late)
                if due_date:
                    late_days = max((datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(due_date, "%Y-%m-%d")).days, 0)
                    fine = late_days * 5  # ₹5 per day
                else:
                    fine = 0  # No fine if no due_date recorded

                # ✅ Fix: Correctly increase the book copies instead of resetting it
                if book_id in self.books:
                    self.books[book_id]["copies"] = int(self.books[book_id]["copies"]) + 1
                    self.save_books()  # Save updated book copies

                # Remove the book from borrow log
                borrow_log.remove(record)
                self.save_borrow_log(borrow_log)

                if fine > 0:
                    return f"Book returned successfully! Late by {late_days} days. Fine: ₹{fine}"
                return "Book returned successfully!"
        
        return "No record of borrowing found!"

