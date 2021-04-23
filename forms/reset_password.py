from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from wtforms.fields.html5 import EmailField


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')