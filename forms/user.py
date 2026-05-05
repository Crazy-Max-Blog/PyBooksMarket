from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    TextAreaField,
    SubmitField,
    EmailField,
    BooleanField,
)
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nickname = StringField("Юзернейм", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired()])
    name = StringField("Имя пользователя", validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField("Зарегестрироваться")


class LoginForm(FlaskForm):
    nickname = EmailField("Юзернейм", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class EditProfileForm(FlaskForm):
    nickname = StringField("Юзернейм", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField("Сохранить")


class EditPasswordForm(FlaskForm):
    password = PasswordField("Старый пароль", validators=[DataRequired()])
    new_password = PasswordField("Новый пароль", validators=[DataRequired()])
    new_password_again = PasswordField(
        "Повторите новый пароль", validators=[DataRequired()]
    )
    submit = SubmitField("Сохранить")
