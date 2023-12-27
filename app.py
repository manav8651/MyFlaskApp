from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
# from data import Articles
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps



app=Flask(__name__)#creating an instance of that class
# Config MySQL with SQLAlchemy
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:9608%40Fury@localhost/myflaskapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: but it's recommended to disable it to reduce overhead

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Articles=Articles() #calling the function in data.py

@app.route('/')
def index():
    return render_template('home.html') 

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    result=db.session.execute(text("SELECT * FROM articles"))
    articles=result.fetchall()
    if result is not None:
        return render_template('articles.html',articles=articles)
    else:
        msg='No Articles Found'
        return render_template('articles.html', msg=msg)

@app.route('/article/<string:id>/')
def article(id):
    result=db.session.execute(text("SELECT * FROM articles WHERE id=:id"),{'id':id})
    article=result.fetchone()

    return render_template('article.html',article=article)

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

#User Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #get data from form
        username=request.form['username'] #no need to use wtforms
        password_candidate=request.form['password']

        result=db.session.execute(text("SELECT * FROM users WHERE username =  :username"), {'username':username})

        data=result.fetchone()
        # data = dict(data) if data else None

        if data is not None:
            # password=data['password']
            # data_dict = {key: data[key] for key in data.keys()}
            data_dict = dict(data._asdict())
            password = data_dict['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in']=True
                session['username']=username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
               error='Invalid Login'
               return render_template('login.html', error=error)
        else:
            error='Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('login'))
        # return f(*args, **kwargs)
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    result=db.session.execute(text("SELECT * FROM articles"))
    articles=result.fetchall()
    if result is not None:
        return render_template('dashboard.html',articles=articles)
    else:
        msg='No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # return render_template('dashboard.html')


class ArticleForm(Form):
    title=StringField('Title', [validators.Length(min=1, max=200)])
    body=TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form=ArticleForm(request.form)
    if request.method=='POST' and form.validate():
        title=form.title.data
        body=form.body.data

        db.session.execute(text("INSERT INTO articles(title, body, author) VALUES(:title, :body, :author)"),{'title':title, 'body':body, 'author':session['username']})
        db.session.commit()
        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    result=db.session.execute(text("SELECT * FROM articles WHERE id= :id"),{'id':id})
    article=result.fetchone()
    form=ArticleForm(request.form)
    article_dict = dict(article._asdict())
    form.title.data=article_dict['title']
    form.body.data=article_dict['body']
    if request.method=='POST' and form.validate():
        title=request.form['title']
        body=request.form['body']

        db.session.execute(text("UPDATE articles SET title= :title, body= :body WHERE id= :id"),{'title':title, 'body':body, 'id':id})
        db.session.commit()
        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)


@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
    db.session.execute(text("DELETE FROM articles WHERE id=:id"),{'id':id})
    db.session.commit()
    flash('Article deleted', 'success')
    return redirect(url_for('dashboard'))

if __name__=='__main__': #to run python application(python app.py)
    app.run(debug=True)#debug=True : will not have to start server again even after changes