from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app=Flask(__name__)#creating an instance of that class
# Config MySQL with SQLAlchemy
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:9608%40Fury@localhost/myflaskapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: but it's recommended to disable it to reduce overhead

# Initialize SQLAlchemy
db = SQLAlchemy(app)


Articles=Articles() #calling the function in data.py

@app.route('/')
def index():
    return render_template('home.html') 

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name=StringField('Name', [validators.Length(min=1, max=50)])
    username=StringField('Username', [validators.Length(min=4, max=25)])
    email=StringField('Email', [validators.Length(min=6, max=50)])
    password=PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm=PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))

        #Inserting into database
        query = text("INSERT INTO users (name, email, username, password) VALUES (:name, :email, :username, :password)")
        db.session.execute(query,{'name':name,'email':email,'username':username,'password':password})
        db.session.commit()
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

if __name__=='__main__': #to run python application(python app.py)
    app.run(debug=True)#debug=True : will not have to start server again even after changes