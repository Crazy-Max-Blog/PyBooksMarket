from flask import Flask, request
from flask import render_template, redirect
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

from werkzeug.datastructures.file_storage import FileStorage

import uuid
import os
import json
import requests

from data import db_session
from data.user import User
from data.book import Book, BookImage
from data.like import Like
from forms.user import RegisterForm, LoginForm, EditProfileForm, EditPasswordForm
from forms.book import BookAddForm, BookEditForm, BookAddImageForm, BookEditImagesForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


# region Home, search


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(User)
    books = db_sess.query(Book)
    try:
        courses = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
        valutes = courses["Valute"]
        usd = valutes["USD"]["Value"]
        euro = valutes["EUR"]["Value"]
    except:
        usd = 0
        euro = 0
    return render_template("index.html", news=news, books=books, usd=usd, euro=euro)


@app.route("/search")
def search():
    query = request.args.get("q", "")
    db_sess = db_session.create_session()
    books = db_sess.query(Book).filter(Book.name.like("%" + query + "%"))
    return render_template("search.html", books=books, query=query)


# region User


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(
            name=form.name.data, nickname=form.nickname.data, about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# region Profile


@app.route("/profile/<string:nickname>")
def profile_id(nickname):
    db_sess = db_session.create_session()
    if nickname[0] == "@":
        nickname = nickname[1:]
        user = db_sess.query(User).filter(User.nickname == nickname)[0]
    else:
        id = int(nickname)
        user = db_sess.query(User).filter(User.id == id)[0]
    books = user.books
    return render_template("profile.html", books=books, user=user)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id)[0]
        user.name = form.name.data
        user.nickname = form.nickname.data
        user.about = form.about.data
        db_sess.commit()
        return redirect("/profile")
    form.name.data = current_user.name
    form.nickname.data = current_user.nickname
    form.about.data = current_user.about
    return render_template("edit_profile.html", form=form)


@app.route("/edit_password", methods=["GET", "POST"])
@login_required
def edit_password():
    form = EditPasswordForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id)[0]
        if not user.check_password(form.password.data):
            return render_template(
                "edit_password.html", form=form, message="Неверный старый пароль"
            )
        if form.new_password.data != form.new_password_again.data:
            return render_template(
                "edit_password.html", form=form, message="Пароли не совпадают"
            )
        user.set_password(form.new_password.data)
        db_sess.commit()
        return redirect("/profile")
    return render_template("edit_password.html", form=form)


@app.route("/profile")
@login_required
def profile():
    return redirect(f"/profile/{current_user.id}")


# region Books


@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = BookAddForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Book(
            name=form.name.data, about=form.about.data, owner_id=current_user.id
        )
        db_sess.add(book)
        db_sess.commit()
        return redirect(f"/edit_images/{book.id}")
    return render_template(
        "book_create.html",
        title="Добавление книги",
        form=form,
        label="Добавление книги",
    )


@app.route("/books/<int:id>")
def book(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    return render_template(
        "book.html", book=book, images=sorted(book.images, key=lambda x: x.position)
    )


@app.route("/books/<int:id>/delete")
def book_delete(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id != current_user.id:
        return redirect(f"/books/{id}")
    db_sess.delete(book)
    db_sess.commit()
    return redirect("/profile")


@app.route("/books/<int:id>/like")
def book_like(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id == current_user.id:
        return redirect(f"/books/{id}")
    book.likes.append(Like(user_id=current_user.id, book_id=id))
    db_sess.commit()
    return redirect(f"/books/{id}")


@app.route("/books/<int:id>/unlike")
def book_unlike(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id == current_user.id:
        return redirect(f"/books/{id}")
    book.likes.remove(
        db_sess.query(Like).filter(Like.user_id == current_user.id, Like.book_id == id)[
            0
        ]
    )
    db_sess.commit()
    return redirect(f"/books/{id}")


@app.route("/books/<int:id>/edit", methods=["GET", "POST"])
def book_edit(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id != current_user.id:
        return redirect(f"/books/{id}")
    form = BookEditForm()
    if form.validate_on_submit():
        book.name = form.name.data
        book.about = form.about.data
        db_sess.commit()
        return redirect(f"/books/{id}")
    form.name.data = book.name
    form.about.data = book.about
    return render_template(
        "book_create.html", book=book, form=form, label="Редактирование книги"
    )


@app.route("/books/<int:id>/add_image", methods=["GET", "POST"])
def book_add_image(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id != current_user.id:
        return redirect(f"/books/{id}")
    form = BookAddImageForm()
    if form.validate_on_submit():
        f: FileStorage = form.imageField.data
        # Create images path if not exists
        if not os.path.exists("static/images/books/"):
            os.makedirs("static/images/books/")
        filename = str(uuid.uuid4().hex) + f.filename
        f.save("static/images/books/" + filename)
        book.images.append(
            BookImage(image=filename, book_id=book.id, position=len(book.images))
        )
        db_sess.commit()
        return redirect(f"/books/{id}")
    return render_template("book_add_image.html", book=book, form=form)


@app.route("/books/<int:id>/delete_image/<int:image_position>", methods=["GET", "POST"])
def book_delete_image(id, image_position):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id != current_user.id:
        return redirect(f"/books/{id}")
    for i in book.images:
        if i.position == image_position:
            book.images.remove(i)
            db_sess.commit()
            return redirect(f"/books/{id}/edit_images")


@app.route("/books/<int:id>/edit_images", methods=["GET", "POST"])
def book_edit_images(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id)[0]
    if book.owner_id != current_user.id:
        return redirect(f"/books/{id}")
    form = BookEditImagesForm()
    if form.validate_on_submit():
        for image in book.images:
            image: BookImage
            print(image.image, form.order.data)
            d = json.loads(form.order.data)
            image.position = d.index(image.image)
            print(image.position)
        db_sess.commit()
        return redirect(f"/books/{id}")
    return render_template(
        "book_edit_images.html",
        book=book,
        form=form,
        images=sorted(book.images, key=lambda x: x.position),
    )


def main():
    db_session.global_init("db.db")
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
