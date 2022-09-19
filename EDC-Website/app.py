

#from operator import truediv
#from pickle import FALSE
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import LoginForm
from flask_login import LoginManager
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from flask_apscheduler import APScheduler
from flask_ckeditor import CKEditor
# from PIL import Image
import os
import shutil
import secrets
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

try:
    os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
except:
    pass


QUESTION_IMAGE_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in QUESTION_IMAGE_ALLOWED_EXTENSIONS


QUESTION_IMAGE_UPLOAD_FOLDER = 'static/question_images'
EXPERT_IMAGE_UPLOAD_FOLDER = 'static/expert_images'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EDC.db'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['QUESTION_IMAGE_UPLOAD_FOLDER'] = QUESTION_IMAGE_UPLOAD_FOLDER
app.config['EXPERT_IMAGE_UPLOAD_FOLDER'] = EXPERT_IMAGE_UPLOAD_FOLDER

ckeditor = CKEditor(app)
bcrypt = Bcrypt(app)
apscheduler = APScheduler()
apscheduler.api_enabled = True
apscheduler.init_app(app)
apscheduler.start()

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(id):
    print(type(id))

    return Expert.query.get(int(id))


class admin(UserMixin):
    def __init__(self, name, id):
        self.name = name
        self.id = id


class Blogs(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

    name = db.Column(db.Text, nullable=False)
    branch = db.Column(db.Text, nullable=False)

    brnch = db.Column(db.String(100))
    imgsrc = db.Column(db.String(100), default='')

    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __repr__(self):
        return 'blogs ' + str(self.id)


class Ideas(db.Model):
    __tablename__ = 'ideas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)

    desc = db.Column(db.Text, nullable=False)
    fund = db.Column(db.Text, nullable=False)
    uname = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    uid = db.Column(db.Integer, nullable=False)
    fund = db.Column(db.Text, nullable=False)
    verified = db.Column(db.Text, nullable=False)
    sold = db.Column(db.Text, nullable=False)

    imgsrc = db.Column(db.String(100), default='')

    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __repr__(self):
        return 'Idea ' + str(self.id)


class Expert(db.Model, UserMixin):
    __tablename__ = 'expert'
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.Text, nullable=False)
    pwd = db.Column(db.Text, nullable=False)
    fname = db.Column(db.Text, nullable=False)
    lname = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    verified = db.Column(db.Integer, default=2)
    subject = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    address = db.Column(db.String(100))
    image = db.Column(db.String(100), default='')
    receipt = db.Column(db.String(100), default='')

    def __repr__(self):
        # return 'expert ' + str(self.id)
        return f"expert( '{self.email}','{self.id}','{self.subject}','{self.fname}','{self.lname}','{self.phone}')"


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)

    news = db.Column(db.Text, nullable=False)
    color = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.utcnow)

    def __repr__(self):
        # return 'expert ' + str(self.id)
        return f"date( '{self.id}')"


class booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    ownerid = db.Column(db.Integer)
    title = db.Column(db.Text)
    details = db.Column(db.Text, default="0")
    done = db.Column(db.Text)

    uid = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    price = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __repr__(self):
        return 'booking ' + str(self.id) + str(self.uid)


@app.route('/')
def index():
    news = News.query.order_by(News.date.desc()).all()
    return render_template('Newindex.html', news=news)


@app.route('/profile')
@login_required
def profile():
    user = Expert.query.get_or_404(current_user.id)
    ideas = Ideas.query.filter(Ideas.uid == current_user.id)

    ideascount = Ideas.query.filter(Ideas.uid == current_user.id).count()
    if current_user.subject == "Investors":
        investedideas = booking.query.filter(
            booking.uid == current_user.id).all()
        ideas = Ideas.query.filter(Ideas.verified == 1).all()

        if len(ideas) == 0:

            isEmpty = True
        else:

            isEmpty = False
        if len(investedideas) == 0:

            isEmptyy = True
        else:

            isEmptyy = False
        return render_template('profile.html', user=user, ideas=ideas, emp=isEmpty, empp=isEmptyy, invidea=investedideas)
    return render_template('profile.html', user=user, ideas=ideas, ideacount=ideascount)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/question_images', picture_fn)
    print(picture_path)
    return picture_fn


def save_pictureexpert(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/expert_images', picture_fn)
    print(picture_path)
    return picture_fn


@app.route('/expertverification', methods=['GET', 'POST'])
@login_required
def expertverification():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":

        experts = Expert.query.all()
        return render_template('expertverification.html', posts=experts)
    return render_template('Newindex.html', news=news)


@app.route('/book/<int:uid>/<int:id>', methods=['GET', 'POST'])
@login_required
def book(uid, id):
    news = News.query.order_by(News.date.desc()).all()
    if current_user.is_authenticated and current_user.subject == "Investors":
        post = Ideas.query.get_or_404(id)
        if request.method == 'POST':
            ownerid = post.uid
            title = post.title

            uid = uid
            pid = id
            name = request.form['questionn']
            email = current_user.email
            price = request.form['op6n']
            mobile = request.form['op7n']
            details = request.form['expn']
            book = booking(title=title, ownerid=ownerid, pid=pid, uid=uid,
                           name=name, mobile=mobile, price=price, email=email, details=details)

            db.session.add(book)
            db.session.commit()
            return redirect('/profile')
        return render_template('book.html', id=id, post=post)
    return render_template('Newindex.html', news=news)


@app.route('/ideaverification', methods=['GET', 'POST'])
@login_required
def ideaverification():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":

        idea = Ideas.query.all()
        return render_template('ideaverification.html', posts=idea)
    return render_template('Newindex.html', news=news)


@app.route('/Idea/<int:id>', methods=['GET', 'POST'])
@login_required
def ideaview(id):
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.is_authenticated:

        idea = Ideas.query.get_or_404(id)
        book = booking.query.filter(booking.pid == id).all()
        return render_template('ideapage.html', post=idea, books=book)
    return render_template('Newindex.html', news=news)


@app.route('/readblog/<int:id>', methods=['GET', 'POST'])
@login_required
def readblog(id):
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.is_authenticated:

        blog = Blogs.query.get_or_404(id)

        return render_template('blogpage.html', post=blog)
    return render_template('Newindex.html', news=news)


@app.route('/expertmanage', methods=['GET', 'POST'])
@login_required
def expertmanage():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":

        experts = Expert.query.filter(
            Expert.subject != "Admin", Expert.verified == 1).all()
        return render_template('expertmanage.html', posts=experts)
    return render_template('Newindex.html', news=news)


@app.route('/managenews', methods=['GET', 'POST'])
@login_required
def managenews():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Technical":

        news = News.query.order_by(News.date.desc()).all()
        return render_template('newsmanage.html', posts=news)
    return render_template('Newindex.html', news=news)


@app.route('/memberpage', methods=['GET', 'POST'])
@login_required
def memberpage():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    # if current_user.subject == "Member":

    news = News.query.order_by(News.date.desc()).all()
    return render_template('memberpage.html', posts=news)
    return render_template('Newindex.html', news=news)


@app.route('/expertupdate', methods=['GET', 'POST'])
@login_required
def expertupdate():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":
        if request.method == 'POST':
            allexpert = Expert.query.filter(
                Expert.subject != "Admin", Expert.verified == 1).all()
            id = request.form.get('id')
            print(id)
            experts = Expert.query.get(request.form.get('id'))
            print(experts.fname)
            experts.email = request.form['email']
            experts.pwd = request.form['password']
            experts.subject = request.form['selsub']
            db.session.commit()
            flash("Update succesfully", "success")
            return render_template('expertmanage.html', posts=allexpert)
    return render_template('Newindex.html', news=news)


@app.route('/addnews', methods=['GET', 'POST'])
@login_required
def addnews():
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Technical":
        allnews = News.query.order_by(News.date.desc()).all()

        if request.method == 'POST':
            news = request.form['news']
            color = request.form['selsub']
            mynews = News(news=news, color=color)
            db.session.add(mynews)
            db.session.commit()
            flash("News Added succesfully", "success")
            return redirect('/managenews')

    return render_template('Newindex.html', news=news)


@app.route('/addidea', methods=['POST'])
@login_required
def addidea():
    # print("hello")

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        fund = request.form['fund']
        uid = current_user.id
        email = current_user.email
        contact = current_user.phone
        uname = current_user.fname+" "+current_user.lname
        verified = "0"
        sold = "0"
        pic = request.files['avatar']

        filename = secure_filename(pic.filename)
    # print(filename+"this is the file name")
        if filename != "":
            # print(request.files)
            pic = request.files['avatar']
            filename = secure_filename(pic.filename)
            fname = save_picture(filename)
            pic.save(os.path.join(
                app.config['QUESTION_IMAGE_UPLOAD_FOLDER'], fname))
        else:
            print("no image")
            fname = ""

        myidea = Ideas(title=title, desc=desc, fund=fund, uid=uid,
                       uname=uname, verified=verified, sold=sold, imgsrc=fname, email=email, phone=contact)
        db.session.add(myidea)
        db.session.commit()
        flash("Idea Added succesfully", "success")
        return redirect('/profile')


@app.route('/deletenews/<int:id>', methods=['GET', 'POST'])
@login_required
def deletenews(id):
    # print("hello")
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Technical":
        news = News.query.get_or_404(id)

        db.session.delete(news)
        db.session.commit()
        flash("News deleted succesfully", "success")
        return redirect('/managenews')

    return render_template('Newindex.html', news=news)


@app.route('/deleteidea/<int:uid>/<int:id>', methods=['GET', 'POST'])
@login_required
def deleteidea(uid, id):
    # print("hello")

    if current_user.id == uid or current_user.subject == "Admin":

        idea = Ideas.query.get_or_404(id)
        book = booking.query.filter(
            booking.pid == id, booking.ownerid == uid).all()
        if (len(book) > 0):
            for bk in book:
                db.session.delete(bk)
                db.session.commit()
        src = idea.imgsrc
    # image_file = url_for('static', filename='question_images/')
        if src != "":
            os.remove(os.path.join(
                app.config['QUESTION_IMAGE_UPLOAD_FOLDER'], src))
        db.session.delete(idea)
        db.session.commit()
        flash("Idea deleted succesfully", "success")
        return redirect('/profile')


@app.route('/deleteinvestor/<int:uid>/<int:id>/<int:pid>', methods=['GET', 'POST'])
@login_required
def delinvestor(uid, id, pid):
    # print("hello")

    if current_user.id == uid:
        idea = Ideas.query.get_or_404(pid)
        idea.sold = "0"
        book = booking.query.get_or_404(id)

        db.session.delete(book)
        db.session.commit()

        flash("Request deleted succesfully", "success")
        return redirect('/profile')


@app.route('/acceptidea/<int:uid>/<int:bid>/<int:id>', methods=['GET', 'POST'])
@login_required
def acceptidea(uid, bid, id):
    # print("hello")

    if current_user.id == uid:

        # book = booking.query.get_or_404(id)
        idea = Ideas.query.get_or_404(id)
        idea.sold = "1"
        book = booking.query.get_or_404(bid)
        book.done = "1"
        db.session.commit()

        flash("Idea Accepted succesfully", "success")
        return redirect('/profile')


@app.route('/rejectidea/<int:uid>/<int:bid>/<int:id>', methods=['GET', 'POST'])
@login_required
def rejectidea(uid, bid, id):
    # print("hello")

    if current_user.id == uid:

        # book = booking.query.get_or_404(id)
        idea = Ideas.query.get_or_404(id)
        idea.sold = "0"
        book = booking.query.get_or_404(bid)
        book.done = "0"
        db.session.commit()

        flash("Idea Rejected succesfully", "success")
        return redirect('/profile')


@app.route('/expertsignup', methods=['GET', 'POST'])
@login_required
def expertsignup():
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":

        if request.method == 'POST':

            firstname = request.form['firstname']
            lastname = request.form['lastname']
            address = request.form['address']
            email = request.form['email']
            phone = request.form['phone']
            pwd = request.form['pwd']
            pic2 = request.files['receipt']
            pic3 = request.files['image']
            sub = request.form['selsub']
            branch = request.form['selbranch']

            filename2 = secure_filename(pic2.filename)
            filename3 = secure_filename(pic3.filename)
            # print(filename+"this is the file name")

        # print(request.files)

            fname2 = save_pictureexpert(filename2)
            fname3 = save_pictureexpert(filename3)

            pic2.save(os.path.join(
                app.config['EXPERT_IMAGE_UPLOAD_FOLDER'], fname2))
            pic3.save(os.path.join(
                app.config['EXPERT_IMAGE_UPLOAD_FOLDER'], fname3))
            expert = Expert(email=email, fname=firstname, lname=lastname, phone=phone,
                            subject=sub, receipt=fname2, address=address, image=fname3, pwd=pwd, verified=2, branch=branch)
            db.session.add(expert)
            db.session.commit()

            return render_template('expertsignup.html')

        else:
            return render_template('expertsignup.html')
    else:
        return render_template('NewIndex.html', news=news)


@app.route('/record', methods=['GET'])
@login_required
def record():
    news = News.query.order_by(News.date.desc()).all()
    # print("hello")
    if current_user.subject == "Admin":
        newscount = News.query.count()
        userno = Expert.query.filter(Expert.verified == 1).count()
        technicalcount = Expert.query.filter(
            Expert.subject == "Technical", Expert.verified == 1).count()

        members = Expert.query.filter(
            Expert.subject == "Member", Expert.verified == 1).all()
        investor = Expert.query.filter(
            Expert.subject == "Investors", Expert.verified == 1).all()
        investorcount = Expert.query.filter(
            Expert.subject == "Investors", Expert.verified == 1).count()
        memberscount = Expert.query.filter(
            Expert.subject == "Member", Expert.verified == 1).count()
        generalsec = Expert.query.filter(
            Expert.subject == "General Secretary", Expert.verified == 1).all()
        generalseccount = Expert.query.filter(
            Expert.subject == "General Secretary", Expert.verified == 1).count()
        president = Expert.query.filter(
            Expert.subject == "President", Expert.verified == 1).all()
        presidentcount = Expert.query.filter(
            Expert.subject == "President", Expert.verified == 1).count()
        technical = Expert.query.filter(
            Expert.subject == "Technical", Expert.verified == 1).all()
        hospitality = Expert.query.filter(
            Expert.subject == "Hospitality", Expert.verified == 1).all()
        hospitalitycount = Expert.query.filter(
            Expert.subject == "Hospitality", Expert.verified == 1).count()
        publicrelation = Expert.query.filter(
            Expert.subject == "Public Relation", Expert.verified == 1).all()
        publicrelationcount = Expert.query.filter(
            Expert.subject == "Public Relation", Expert.verified == 1).count()
        treasurer = Expert.query.filter(
            Expert.subject == "Treasurer", Expert.verified == 1).all()
        treasurercount = Expert.query.filter(
            Expert.subject == "Treasurer", Expert.verified == 1).count()
        organizing = Expert.query.filter(
            Expert.subject == "Organizing", Expert.verified == 1).all()
        organizingcount = Expert.query.filter(
            Expert.subject == "Organizing", Expert.verified == 1).count()
        social = Expert.query.filter(
            Expert.subject == "Social Media", Expert.verified == 1).all()
        socialcount = Expert.query.filter(
            Expert.subject == "Social Media", Expert.verified == 1).count()
        creative = Expert.query.filter(
            Expert.subject == "Creative", Expert.verified == 1).all()
        creativecount = Expert.query.filter(
            Expert.subject == "Creative", Expert.verified == 1).count()

        return render_template('record.html', technical=technical, members=members, generalsec=generalsec, president=president, hospitality=hospitality, publicrelation=publicrelation, treasurer=treasurer, organizing=organizing, creative=creative, social=social, users=userno, technicalcount=technicalcount,
                               membc=memberscount, generalsecc=generalseccount, presidentc=presidentcount, hospitalityc=hospitalitycount, publicrelationc=publicrelationcount, treasurerc=treasurercount, organizingc=organizingcount, creativec=creativecount, socialc=socialcount, newscount=newscount, member=members, investor=investor, investorcount=investorcount)
    return render_template('Newindex.html', news=news)


@app.route('/expert/edit/<int:id>/<string:sub>/<string:email>', methods=['POST'])
@login_required
def expertedit(id, email, sub):
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":
        email = email
        post = Expert.query.get_or_404(id)

        if request.method == 'POST':

            verify = request.form['inlineRadioOptionsnn'+str(email)]
            print(verify)

            post.verified = request.form['inlineRadioOptionsnn'+str(email)]
            if verify == "1":

                user = Expert.query.get_or_404(id)

                user.verify = 1
                db.session.commit()
            else:
                user = Expert.query.get_or_404(id)
                user.verify = 0
                db.session.commit()
            db.session.commit()
            return redirect('/expertverification')

    return render_template('Newindex.html', news=news)


@app.route('/adminverify/<int:id>/<string:email>', methods=['POST'])
@login_required
def expertverify(id, email):
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":

        post = Ideas.query.get_or_404(id)

        if request.method == 'POST':

            verify = request.form['inlineRadioOptionsnn'+str(email)]
            print(verify)

            post.verified = request.form['inlineRadioOptionsnn'+str(email)]
            if verify == "1":

                user = Ideas.query.get_or_404(id)

                user.verify = 1
                db.session.commit()
            else:
                user = Ideas.query.get_or_404(id)
                user.verify = 0
                db.session.commit()
            db.session.commit()
            return redirect('/ideaverification')

    return render_template('Newindex.html', news=news)


@app.route('/expert/delete/<int:id>')
@login_required
def expertdelete(id):
    news = News.query.order_by(News.date.desc()).all()
    if current_user.subject == "Admin":

        post = Expert.query.get_or_404(id)

    #  if request.method == 'POST':

        src2 = post.receipt
        src3 = post.image

        if src2 != "" and src3 != "":
            print("userdeleted")

            os.remove(os.path.join(
                app.config['EXPERT_IMAGE_UPLOAD_FOLDER'], src2))
            os.remove(os.path.join(
                app.config['EXPERT_IMAGE_UPLOAD_FOLDER'], src3))
            db.session.delete(post)
            db.session.commit()

        db.session.commit()

        return redirect('/expertverification')

    return render_template('Newindex.html', news=news)


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    if current_user.subject == "Creative":
        loggedid = True
    else:
        loggedid = False
    if request.method == 'POST':
        # if "file" not in request.files:
        #     flash("no files apart", "danger")
        #     return redirect(url_for('new_post'))
        pic = request.files['avatar']

        filename = secure_filename(pic.filename)
    # print(filename+"this is the file name")
        if filename != "":
            # print(request.files)
            pic = request.files['avatar']
            filename = secure_filename(pic.filename)
            fname = save_picture(filename)
            pic.save(os.path.join(
                app.config['QUESTION_IMAGE_UPLOAD_FOLDER'], fname))
        else:
            print("no image")
            fname = ""

        # print(pic)

        post_title = request.form['question']

        post_sub = request.form['selsub']
    # print(post_sub)
        name = request.form['op1']
        branch = request.form['op2']

        new_post = Blogs(title=post_title,  name=name,
                         branch=branch, brnch=post_sub, imgsrc=fname)
        db.session.add(new_post)
        db.session.commit()
        flash("Post added successfully", "success")
        return redirect('/posts')
    else:
        image_file = url_for('static', filename='question_images/')
        all_posts = Blogs.query.order_by(Blogs.date_posted.desc()).all()
        if len(all_posts) == 0:
            isEmpty = True
        else:
            isEmpty = False
        return render_template('posts.html',
                               posts=all_posts, img=image_file, loggedid=loggedid, emp=isEmpty
                               )


@app.route('/sub', methods=['GET', 'POST'])
def subs():
    if current_user.subject == "Creative":
        loggedid = True
    else:
        loggedid = False
    if request.method == 'POST':

        subs = request.form['selsubbb']
        print(type(subs))
        if str(subs) == "RR":

            #   all_posts = QuestionPost.query.order_by(QuestionPost.date_posted).all()
            return redirect(url_for('posts'))
        else:
            all_posts = Blogs.query.filter_by(brnch=subs).all()
            print(type(all_posts))
            if len(all_posts) == 0:
                isEmpty = True
            else:
                isEmpty = False
            return render_template('posts.html', posts=all_posts, loggedid=loggedid, emp=isEmpty)
    else:
        all_posts = Blogs.query.order_by(Blogs.date_posted).all()
        return render_template('posts.html', posts=all_posts, loggedid=loggedid)


@app.route('/posts/delete/<int:id>')
@login_required
def delete(id):
    news = News.query.order_by(News.date.desc()).all()
    if current_user.is_authenticated and (current_user.subject == "Creative" or current_user.role == "Technical"):

        post = Blogs.query.get_or_404(id)
        src = post.imgsrc
    # image_file = url_for('static', filename='question_images/')
        if src != "":
            os.remove(os.path.join(
                app.config['QUESTION_IMAGE_UPLOAD_FOLDER'], src))
        db.session.delete(post)
        db.session.commit()
        return redirect('/posts')
    return render_template('Newindex.html', news=news)


@app.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():

    return render_template('new_post.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('adminposts'))
    form = LoginForm()
    if form.validate_on_submit():
        # if form.email.data == 'admin@site.this' and form.password.data == 'password123':
        #     flash('You have been logged in!', 'success')
        #     user = admin("Expert",int(1212121212121))
        #     login_user(user)

        #     return redirect('/adminposts')

        # else:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = Expert.query.filter_by(email=form.email.data).first()
            if user and (user.pwd == form.password.data and user.verified == 1):
                print("loggedin")
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    #     else:
        # flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@apscheduler.task('interval', id='tmp_deletion_job', minutes=5, misfire_grace_time=900)
def clean_tmp_folder():
    folder = 'tmp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            pass


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    # apscheduler.start()
    app.run(debug=True)
