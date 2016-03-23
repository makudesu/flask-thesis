from flask import Flask, render_template, flash, request, url_for, redirect, session, Response
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from flask.ext.login import UserMixin, LoginManager, login_required, login_user
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import Required, EqualTo

from flask.ext.sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from passlib.hash import sha256_crypt
import gc

"""config"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '128JSD*idfedf8ued89f7JHEDFjtw1143589123849iU*(UDF*D*F()D*F)(D*fjsdjfkj238490sdjfkjJDJFi(*)(&^&^*%tYYGHGhjBBb*H*hffJghgdfhkjk3eio2u3oiuqwoieuoiqyopolavofuiekghogsjdb*&&&DFOD&*F*(D&F*(DIOFUIKFHJDJHCKJVHJKCVkchvuhyiudyf8s9df98789743124789238UIOuFKAHDFKJAHDKLASHjkdgasgdhhasdgkjashdU(*&(*&*(*^^ASd876a7s6d87&&$^%$^#<F2>3234$#@121432!$25434%79^)*X&D(97_(A*Sd09POJZXd'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost/thesis"
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
#login_manager.login_view = 'users.login'
Bootstrap(app)
db = SQLAlchemy(app)

class RegisterForm(Form):
    username = StringField('username', validators=[Required()])

    password = PasswordField('Password', validators=[
        Required(),
        EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Confirm Password', validators=[Required()])

    account_type = SelectField(u'Account Type', choices = [
        ('Stud', 'Student'),
        ('Admi', 'Admin')
        ],
        validators=[Required()])
    student_status = SelectField(u'Student Type', choices = [
        ('New', 'New Student'), 
        ('Trans', 'Transferee')
        ],
        validators=[Required()])
    other_details = StringField('Other Registration details like age or something', validators=[Required()])
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

"""models"""
class User(UserMixin, db.Model):
    #TYPES = [
    #    (u'admin', u'Admin'),
    #    (u'student', u'Student')
    #]
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    stud_id = db.Column(db.Integer, db.ForeignKey('student.stud_id'),nullable=True) 
    account_type = db.Column(db.String(64))

    def __init(self, username, password):
        self.username = username
        self.password = password
    
    @classmethod
    def get(cls,id):
        return cls.User.get(int(user_id))

    def __repr__(self):
        return "User %s" % self.username

class Student(db.Model):
    stud_id = db.Column(db.Integer, primary_key=True)
    registrations = db.relationship('Registration', backref='student')
    user = db.relationship('User', backref='student')
    student_status = db.Column(db.String(64))
    other_details = db.Column(db.String(64))

    def __repr__(self):
        return "Student %d" % self.stud_id

class Registration(db.Model):
    reg_id = db.Column(db.Integer, primary_key=True)
    school_year = db.Column(db.String(64))
    grade_level = db.Column(db.Integer, default='6')
    year_level_status = db.Column(db.String(10))
    stud_id = db.Column(db.Integer, db.ForeignKey('student.stud_id'), nullable=True)
#
    def __repr__(self):
        return "Registration %d" % self.reg_id

@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":") # naive token
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None

@login_manager.unauthorized_handler
def unauthorized():
    flash('Unauthorized! Get out of here before I get mad, or you could just login/register.' )
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))    
"""forms"""

"""routes"""
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=form.password.data)
        if user.count() !=1:
            flash('Wrong Username and/or Password')
            return render_template('signin.html', form=form)
        login_user(user[0])
        flash('Login Successful')
    return render_template('signin.html', form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exclusive/')
@login_required
def exclusive():
    return render_template('index.html')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
    username = form.username.data
    password = form.password.data,
    account_type = form.account_type.data
    student_status = form.student_status.data
    other_details = form.other_details.data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user == None:
            student = Student(
                        student_status = form.student_status.data,
                        other_details =  form.other_details.data
                        )
            db.session.add(student)
            db.session.commit()
            # you get the error TypeError: coercing to Unicode: need string or buffer, long found because of None
            #if mild:
            #    flash('stud_id is true')
            #user = User(
            #            username = form.username.data,
            #            password = sha256_crypt.encrypt((str(form.password.data))),
            #            account_type = form.account_type.data,
            #            stud_id = mild
            #            )
            #db.session.add(user)
            #db.session.commit()
            flash('Registration Successful')
            return redirect(url_for('index'))
        else:
            flash('The username is already taken')
    return render_template('signup.html', form=form, username=username, password=password, account_type=account_type, student_status=student_status, other_details=other_details)
#


class StudentView(ModelView):
    page_size = 10

admin = Admin(app, name='Bnhs', template_mode='bootstrap3', index_view=None)
admin.add_view(StudentView(Student, db.session))
admin.add_view(StudentView(Registration, db.session))
admin.add_view(StudentView(User, db.session))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

