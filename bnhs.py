from flask import Flask, render_template, flash, request, url_for, redirect, session, Response
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from flask.ext.login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import Required, EqualTo

from flask.ext.sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

"""config"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '128JSD*idfedf8ued89f7JHEDFjtw1143589123849iU*(UDF*D*F()D*F)(D*fjsdjfkj238490sdjfkjJDJFi(*)(&^&^*%tYYGHGhjBBb*H*hffJghgdfhkjk3eio2u3oiuqwoieuoiqyopolavofuiekghogsjdb*&&&DFOD&*F*(D&F*(DIOFUIKFHJDJHCKJVHJKCVkchvuhyiudyf8s9df98789743124789238UIOuFKAHDFKJAHDKLASHjkdgasgdhhasdgkjashdU(*&(*&*(*^^ASd876a7s6d87&&$^%$^#<F2>3234$#@121432!$25434%79^)*X&D(97_(A*Sd09POJZXd'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost/thesis"
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://vwuktasevlatqt:c-gzQ-avJEw5mlufChylQ25OKy@ec2-54-204-30-115.compute-1.amazonaws.com:5432/d8gppbdark5i8f"
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
login_manager.login_view = 'login'
Bootstrap(app)
db = SQLAlchemy(app)

"""wrapper"""
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already logged in. You can't login/register while logged in.")
            return redirect(url_for('user'))
        return f(*args, **kwargs)
    return decorated_function

class RegisterForm(Form):
    username = StringField('username', validators=[Required()])
    password = PasswordField('Password', validators=[
        Required(),
        EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Confirm Password', validators=[Required()])
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


class EnrollForm(Form):
    username = StringField('username', validators=[Required()])
    other_details= StringField('Other Details', validators=[Required()])
    submit = SubmitField('Save')

class EnrollmentForm(Form):
    submit = SubmitField('enroll')

"""models"""
class User(UserMixin, db.Model):
    #TYPES = [
    #    (u'admin', u'Admin'),
    #    (u'student', u'Student')
    #]
    stud_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    user = db.relationship('Registration', backref='registration')
    student_status = db.Column(db.String(64))
    other_details = db.Column(db.String(64))
    authenticated = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(64), default='Student')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def get_id(self):
        return self.stud_id

    def is_authenticated(self):
        return self.authenticated

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return self.username

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_year = db.Column(db.String(64))
    grade_level = db.Column(db.Integer, default='6')
    year_level_status = db.Column(db.String(10))
    stud_id = db.Column(db.Integer, db.ForeignKey('user.stud_id'), nullable=True)
    current = db.Column(db.Boolean, default=True)
#
    def __repr__(self):
        return str(self.id)

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
        return User.query.get(user_id)    
"""forms"""

"""routes"""
@app.route('/login/', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Wrong Username and/or Password')
    return render_template('signin.html', form=form)

@app.route('/logout/')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('You have been logged out.')
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/user/', methods=['GET', 'POST'])
@login_required
def user():
    user = User.query.filter_by(username=current_user.username).first()
    form = EnrollForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('user.html', user=user, form=form
        )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exclusive/')
@login_required
def exclusive():
    return render_template('index.html')

@app.route('/enroll/', methods=['GET', 'POST'])
@login_required
def enroll():
    user = User.query.filter_by(username=current_user.username).first()
    grade = user.student_status
    grad_status = Registration.query.filter_by(stud_id = current_user.stud_id).filter_by(current = True).first()
    print grad_status.year_level_status
   # .year_level_status
#    grade_stat = grader.query.filter_by(current = True).first()
#    print grade_stat.year_level_status, grade_stat.registration, grade_stat.current
#    print grader.registration, grader.current, grader.year_level_status

#    grade_status = Registration.query.filter_by(stud_id=current_user.stud_id).first()
#    print grade_status.year_level_status
    if grade == "Trans":
        flash("Pwede kang magenroll ng kahit aling grade")
    elif grade == "Old":
        flash("Pwede kang magenroll ng next grade kung pasado ka. Pero kung hindi, makiusap ka sa titser mo para ipasa ka.")
        if grad_status.year_level_status == 'Enrolled':
            flash('You are already enrolled')
        if grad_status.year_level_status == 'Passed':
            flash('Congratuletsion pasado ka.')
        if grad_status.year_level_status == 'Failed':
            flash('Unfortunately you failed.')

    elif grade =='New':
        flash('You are enrolled in Grade 7')
        enrolle = Registration(
                    stud_id = user.stud_id,
                    grade_level = '7',
                    year_level_status = 'Enrolled'
                    )
        current_user.student_status = 'Old'
        db.session.add(user)
        db.session.add(enrolle)
        db.session.commit()
    return render_template('index.html')
#


@app.route('/signup/', methods=['GET', 'POST'])
@logout_required
def signup():
    form = RegisterForm(request.form)
    username = form.username.data
    password = form.password.data,
    student_status = form.student_status.data
    other_details = form.other_details.data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username is already taken.')
            return render_template('signup.html', form=form, username=username, password=password, student_status=student_status, other_details=other_details)
        user = User(
                    username = form.username.data,
                    password = form.password.data,
                    student_status = form.student_status.data,
                    other_details =  form.other_details.data
                    )
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful')
        return redirect(url_for('index'))
    return render_template('signup.html', form=form, username=username, password=password, student_status=student_status, other_details=other_details)
#


class TableView(ModelView):
    page_size = 10

admin = Admin(app, name='Bnhs', template_mode='bootstrap3', index_view=None)
admin.add_view(TableView(User, db.session))
admin.add_view(TableView(Registration, db.session))

if __name__ == '__main__':
#    db.drop_all()
    db.create_all()
    app.run(debug=True)

