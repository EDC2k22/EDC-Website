

from flask import Flask,render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField,ValidationError
from wtforms.validators import DataRequired,EqualTo,Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_migrate import Migrate
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
app = Flask(__name__)
#WTF forms csrf key
app.config['SECRET_KEY']="afndonfi6612@"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'

#database******************
db=SQLAlchemy(app)
migrate=Migrate(app,db)
# model
class Users(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False)
    name=db.Column(db.String(200),nullable=False)
    email=db.Column(db.String(120),nullable=False,unique=True)
    event=db.Column(db.Integer,primary_key=True)

    date_added=db.Column(db.DateTime,default=datetime.utcnow)
    #password_hash
    password_hash=db.column(db.String(128))

    @property
    def password(self):
        raise AttributeError("password is not readable")
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    # string 
    def __repr__(self):
        return '<Name %r>' % self.name

class UserForm(FlaskForm):
    username=StringField("UserName: ",validators=[DataRequired()])
    name=StringField("Name: ",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired()])
    password_hash=PasswordField('Password',validators=[DataRequired(),EqualTo('passwor_hash2',message='password must match')])
    password_hash2=PasswordField('Confirm Password',validators=[DataRequired()])
    submit=SubmitField("submit")      


@app.route('/user/add',methods=['GET','POST'])
def add_user():
    name=None
    form=UserForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hash
            hashed_pw=generate_password_hash(form.password_hash.data,"sha256")
            user=Users(username=form.username.data,name=form.name.data,email=form.email.data,password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.username.data=''
        form.email.data=''
        form.password_hash.data=''
        flash("added successfully")
    our_users=Users.query.order_by(Users.date_added)
    return render_template("add_user.html",form=form,name=name,our_users=our_users
    )
# Update database record***********
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    form=UserForm()
    name_to_update=Users.query.get_or_404(id)
    if request.method== "POST":
        name_to_update.name=request.form['name']
        name_to_update.email=request.form['email']
        try:
            db.session.commit()
            flash("Update successful")
            return render_template("update.html",form=form,name_to_update=name_to_update)
        except:
            flash("Try again")
            return render_template("update.html",form=form,name_to_update=name_to_update)
    else:
         return render_template("update.html",form=form,name_to_update=name_to_update,id=id)

# delete database*************

@app.route('/delete/<int:id>')
def delete(id):
    name=None
    form=UserForm
    user_to_delete=Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("deleted successfully")
        our_users=Users.query.order_by(Users.date_added)
        return render_template("add_user.html",form=form,name=name,our_users=our_users)
    except:
        flash("Error")
        return render_template("add_user.html",form=form,name=name,our_users=our_users)

# Login******************
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='view'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("submit")

@app.route("/login",methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("login successful")
                return redirect({{url_for('dashboard')}})
            else:
                flash("Wrong password")
        else:
            flash("No such user.")
    return render_template('login.html',form=form)

@app.route("/dashboard",methods=['GET','POST'])
# @login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("logged out")
    return redirect(url_for('login'))









# **********************
class NameForm(FlaskForm):
    name=StringField("Name: ",validators=[DataRequired()])
    submit=SubmitField("submit")
@app.route("/form",methods=['GET','POST'])
def Form():
    name=None
    form=NameForm()
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
        #message*****************
        flash("Form submitted successfully")
    return render_template("WTF.html",name=name,form=form)

# *********************
@app.route("/index")
def hello_world():
    return render_template("index.html")

@app.route("/user/<name>")
def User(name):
    return render_template("user.html",name=name)
#create error pages*****
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
@app.errorhandler(500)
def page_not_foundInternal(e):
    return render_template("500.html"),500


# Main login page 

if __name__=="__main__":
    app.run(debug=True)