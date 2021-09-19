from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class SigUpForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Sign up')

class IDNumber(FlaskForm):
    id_number = StringField('number')
    submit = SubmitField('select')