#This module is for database models
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
from flask_login import UserMixin


#Initialization of database
db = SQLAlchemy()

#Creating a user db model
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
#Creating an expense db model
class Expense(db.Model):  #Add db.Model
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

#Creating a category db model
class Category(db.Model):  #Add db.Model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    expenses = db.relationship("Expense", backref='category', lazy=True)

