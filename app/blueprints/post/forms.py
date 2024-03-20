from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField
from wtforms.validators import DataRequired





class CreateEventPost(FlaskForm):
    img_url = StringField('img_url', validators=[DataRequired()])
    caption = StringField('caption', validators=[DataRequired()])  
    location= StringField('location', validators=[DataRequired()])  
    submit_btn = SubmitField('create event post')


class CreatePost(FlaskForm):
    img_url = StringField('img_url', validators=[DataRequired()])
    caption = StringField('caption', validators=[DataRequired()])  
    location= StringField('location', validators=[DataRequired()])  
    submit_btn = SubmitField('create post')
