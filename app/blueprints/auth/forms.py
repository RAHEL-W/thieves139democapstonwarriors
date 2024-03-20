from flask_wtf import FlaskForm
from wtforms import EmailField,PasswordField, SubmitField,StringField
from wtforms.validators import DataRequired





class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])  
    submit_btn = SubmitField('log in')


class SignupForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit_btn = SubmitField('signup')
      