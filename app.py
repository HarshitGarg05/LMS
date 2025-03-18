from flask import Flask, render_template, request, redirect, session
from datetime import date,datetime
from database import Database

app = Flask(__name__)
app.secret_key = "library_secret_key"

db = Database()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_type = request.form["user_type"]
        user_id = request.form["user_id"]
        name = request.form["name"]
        password = request.form["password"]

        if db.register_user(user_id, name, password, user_type):
            session["user_id"] = user_id
            session["user_type"] = user_type
            return redirect("/dashboard")
        else:
            return render_template("register.html", error="User ID already exists!")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        user = db.authenticate_user(user_id, password)
        if user:
            session["user_id"] = user_id
            session["user_type"] = user["user_type"]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials!")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_type = session["user_type"]
    books = db.get_all_books()
    borrow_log = db.load_borrow_log()
    today = date.today().strftime("%Y-%m-%d")  # Ensure today is in the correct format

    # Convert due_date to a string with YYYY-MM-DD format
    for record in borrow_log:
        if "due_date" in record:
            record["due_date"] = datetime.strptime(record["due_date"], "%Y-%m-%d").strftime("%Y-%m-%d")

    if user_type == "student":
        return render_template("student_dashboard.html", books=books, borrow_log=borrow_log, today=today)
    elif user_type == "librarian":
        return render_template("librarian_dashboard.html", books=books)

    return redirect("/login")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if "user_id" not in session or session["user_type"] != "librarian":
        return redirect("/login")

    if request.method == "POST":
        book_id = request.form["book_id"]
        title = request.form["title"]
        author = request.form["author"]
        copies = request.form["copies"]

        message = db.add_book(book_id, title, author, copies)
        return render_template("add_book.html", message=message)

    return render_template("add_book.html")

@app.route("/edit_book/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if "user_id" not in session or session["user_type"] != "librarian":
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        copies = request.form["copies"]

        message = db.edit_book(book_id, title, author, copies)
        return redirect("/dashboard")

    book = db.books.get(book_id)
    return render_template("edit_book.html", book=book, book_id=book_id)

@app.route("/delete_book/<book_id>")
def delete_book(book_id):
    if "user_id" not in session or session["user_type"] != "librarian":
        return redirect("/login")

    db.delete_book(book_id)
    return redirect("/dashboard")


@app.route("/borrow/<book_id>")
def borrow(book_id):
    if "user_id" not in session or session["user_type"] != "student":
        return redirect("/login")

    message = db.borrow_book(session["user_id"], book_id)
    return redirect("/dashboard")

@app.route("/return/<book_id>")
def return_book(book_id):
    if "user_id" not in session or session["user_type"] != "student":
        return redirect("/login")

    message = db.return_book(session["user_id"], book_id)
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
