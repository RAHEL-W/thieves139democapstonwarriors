from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField,StringField
from wtforms.validators import DataRequired





class InviteForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    caption = StringField('caption', validators=[DataRequired()])
    submit_btn = SubmitField('invite frends')



      