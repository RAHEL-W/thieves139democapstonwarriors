
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from datetime import datetime


db = SQLAlchemy()




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String, unique=True, nullable=False)
    email = db.Column (db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    posts = db.relationship('Post', backref='author')
    save_games = db.relationship('SaveGame', backref='author')


    def __init__(self,  username,  email,password):
        
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def save(self):
        db.session.add(self)
        db.session.commit()  

   






class Post(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    img_url=db.Column(db.String, nullable=False) 
    caption = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)  
    date =  db.Column(db.DateTime, default=datetime.utcnow(),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False )  

    def  __init__(self, img_url, caption, location, user_id):
        self.img_url = img_url
        self.caption = caption
        self.location = location
        self.user_id = user_id




    def save(self):
        db.session.add(self)
        db.session.commit()


class SaveGame(db.Model):
    date=db.Column(db.String, primary_key=True)
    opponent=db.Column(db.String,  nullable=False)
    opponent2=db.Column(db.String,  nullable=False)
    opponent_img=db.Column(db.String(300),  nullable=False)
    opponent_img2= db.Column(db.String(300),  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False ) 
    def __init__(self,date ,opponent, opponent2, opponent_img,opponent_img2,user_id):
        self.date=date
        self.opponent = opponent
        self.opponent2 = opponent2
        self.opponent_img = opponent_img
        self.opponent_img2 = opponent_img2
        self.user_id = user_id
    def save(self):  
        db.session.add(self)  
        db.session.commit() 
            