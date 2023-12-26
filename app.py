from flask import Flask, render_template

app=Flask(__name__)#creating an instance of that class

@app.route('/')
def index():
    return render_template('home.html') 

@app.route('/about')
def about():
    return render_template('about.html')

if __name__=='__main__': #to run python application(python app.py)
    app.run(debug=True)#debug=True : will not have to start server again even after changes