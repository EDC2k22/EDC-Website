from turtle import title
from flask import Flask,render_template,url_for
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/Event')
def Event():
    return render_template('Event.html',title='Event & Workshops')

@app.route('/About')
def About():
    return render_template('About.html',title='About us')

@app.route('/History&Achievements')
def History():
    return render_template('History.html',title='History & Achievements')

if __name__=="__main__":
    app.run(debug=True,port=8000)