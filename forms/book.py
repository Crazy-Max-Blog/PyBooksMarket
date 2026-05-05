from flask_wtf import FlaskForm
from flask_uploads import UploadSet, IMAGES
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    HiddenField,
)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired

images = UploadSet("images", IMAGES)


class BookAddForm(FlaskForm):
    name = StringField("Название книги", validators=[DataRequired()])
    about = TextAreaField("Немного о книге")
    submit = SubmitField("Создать")


class BookEditForm(FlaskForm):
    name = StringField("Название книги", validators=[DataRequired()])
    about = TextAreaField("Немного о книге")
    submit = SubmitField("Сохранить")


class BookAddImageForm(FlaskForm):
    imageField = FileField(
        "Добавить изображение", validators=[FileRequired()]
    )  # , FileAllowed(IMAGES, 'Только изображения!')])
    # imageField.accept="image/*"
    submit = SubmitField("Сохранить")


class BookEditImagesForm(FlaskForm):
    order = HiddenField()  # Порядок изображений
    submit = SubmitField("Сохранить")
