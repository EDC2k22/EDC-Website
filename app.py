from turtle import title
from flask import Flask, render_template, url_for
app = Flask(__name__)


@app.route('/')
@app.route('/Home')
def Home():
    return render_template("Home.html", title='Home')


@app.route('/Event')
def Event():
    return render_template('Event.html', title='Event & Workshops')


@app.route('/About')
def About():
    return render_template('About.html', title='About us')


@app.route('/History&Achievements')
def History():
    return render_template('History.html', title='History & Achievements')


@app.route('/Admindashboard')
def Admindashboard():
    return render_template('Admindashboard.html', title='Admin Dashboard')


@app.route('/Members')
def Members():
    return render_template('Members.html', title='EDC Members')


@app.route('/Profile')
def Profile():
    return render_template('Profile.html', title='Member profile')


@app.route('/login')
def Login():
    return render_template('login.html', title='Member profile')


if __name__ == "__main__":
    app.run(debug=True, port=8000)
