from flask import Flask, render_template, flash, request, url_for, redirect, session, Response
from flask.ext.bootstrap import Bootstrap
from flask_wtf import Form, RecaptchaField
from flask.ext.login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user, AnonymousUserMixin
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, IntegerField, DateField
from wtforms.validators import Required, EqualTo

from flask.ext.sqlalchemy import SQLAlchemy

from flask_admin import Admin, BaseView
from flask.ext.admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView 

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

"""config"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '128JSD*idfedf8ued89f7JHEDFjtw1143589123849iU*(UDF*D*F()D*F)(D*fjsdjfkj238490sdjfkjJDJFi(*)(&^&^*%tYYGHGhjBBb*H*hffJghgdfhkjk3eio2u3oiuqwoieuoiqyopolavofuiekghogsjdb*&&&DFOD&*F*(D&F*(DIOFUIKFHJDJHCKJVHJKCVkchvuhyiudyf8s9df98789743124789238UIOuFKAHDFKJAHDKLASHjkdgasgdhhasdgkjashdU(*&(*&*(*^^ASd876a7s6d87&&$^%$^#<F2>3234$#@121432!$25434%79^)*X&D(97_(A*Sd09POJZXd'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://ljaavoeziccuxy:R1AYt8nzTJLR5tC-BfaM3fZ6sg@ec2-54-225-112-119.compute-1.amazonaws.com:5432/d9hrf2d6n9ifu9"
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost/thesis"
"""set the school year"""
app.config['CSY'] = '2016-2017'
"""set the enrollment"""
app.config['Enrollment'] = True
#recaptcha
app.config['RECAPTCHA_USE_SSL'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdyyB4TAAAAAMLx8wYShiHU3AsSbRCBdFnp8L1N'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdyyB4TAAAAAMtj9CGXKjuOBN3RflEWaXacx-t3'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://vwuktasevlatqt:c-gzQ-avJEw5mlufChylQ25OKy@ec2-54-204-30-115.compute-1.amazonaws.com:5432/d8gppbdark5i8f"
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.init_app(app)
login_manager.login_view = 'login'
Bootstrap(app)
db = SQLAlchemy(app)
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Idiot'
        self.role = 'idiot'
login_manager.anonymous_user = Anonymous

"""wrapper"""
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already logged in. You can't login/register while logged in.")
            return redirect(url_for('user'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.unauthorized_handler
def unauthorized():
    flash('Unauthorized! Get out of here before I get mad, or you could just login/register.' )
    return redirect(url_for('login', next=request.url))

class IsAdminMenuLink(MenuLink):

    def is_accessible(self):
        return current_user.role == 'Admin' or current_user.role == 'Teacher'

class IsnotLoggedinMenuLink(MenuLink):
    
    def is_accessible(self):
        return current_user.is_authenticated == False

"""forms"""
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
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

class LoginForm(Form):
    username = StringField('username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class EnrollForm(Form):
    username = StringField('Username', validators=[Required()])

    last_name = StringField('Last Name', validators=[Required()])
    first_name = StringField('First Name', validators=[Required()])
    middle_name = StringField('Middle Name', validators=[Required()])
    gender = StringField('Gender', validators=[Required()])
    birth_date = StringField('Birth Date', validators=[Required()])
    age = StringField('Age', validators=[Required()])
    birth_place = StringField('Birth Place', validators=[Required()])
    religion = StringField('Religion', validators=[Required()])
    present_address = StringField('Present Address', validators=[Required()])
    email = StringField('Email', validators=[Required()])
    contact_number = IntegerField('Contact Number', validators=[Required()])

    submit = SubmitField('Save')

class EnrollmentForm(Form):
    grade_level = SelectField('Grade Level', choices = [
        ('7', 'Grade 7'), 
        ('8', 'Grade 8'), 
        ('9', 'Grade 9'), 
        ('10', 'Grade 10'), 
        ('11', 'Grade 11'), 
        ('12', 'Grade 12')
        ],
        validators=[Required()])
    submit = SubmitField('Enroll')

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

    last_name = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    middle_name = db.Column(db.String(64))
    gender = db.Column(db.String(64))
    birth_date = db.Column(db.String(64))
    age = db.Column(db.Integer)
    birth_place = db.Column(db.String(64))
    religion = db.Column(db.String(64))
    present_address = db.Column(db.String(64))
    email = db.Column(db.String(64))
    contact_number = db.Column(db.Integer)
    role = db.Column(db.String(64), default='Student')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def get_id(self):
        return self.stud_id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

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
    
    def __repr__(self):
        return str(self.id)
"""flask-login"""
@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":") 
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None

@login_manager.user_loader
def load_user(user_id):
        return User.query.get(user_id)    

"""routes"""
@app.route('/')
def index():
    print app.config['CSY']
    return render_template('index.html')

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
            if current_user.role == 'Admin':
                return redirect(url_for('admin.index'))
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

class EnrollmentLogic:

    def __init__(self):
        self.grad_status = Registration.query.filter_by(stud_id = current_user.stud_id).filter_by(current = True).first()
        self.user = User.query.filter_by(username=current_user.username).first()
        self.grade = self.user.student_status
        self.enrollee = Registration(
            school_year = app.config['CSY'],
            stud_id = self.user.stud_id,
            grade_level = self.next_level(),
            year_level_status = 'Enrolled'
        )

    def is_admin(self):
        if current_user.role == 'Admin':
            return True

    def grade_status_is_none(self):
        if self.grad_status is None:
            return True

    def is_transferee(self):
        if self.grade  == str('New') or self.grade == str('Old'):
            return True

    def grade_trans(self):
        if self.grade == "Trans":
            return True

    def grade_new(self):
        if self.grade == "New":
            return True

    def grade_old(self):
        if self.grade == "Old":
            return True

    def is_enrolled(self):
        if self.grad_status.year_level_status == 'Enrolled':
            return True

    def is_passed(self):
        if self.grad_status.year_level_status == 'Passed':
            return True

    def is_failed(self):
        if self.grad_status.year_level_status == 'Failed':
            return True

    def is_graduate(self):
        if self.grad_status.grade_level >= int(12):
            return True

    def next_level(self):
        self.next_grade_level = int(7)
        current_user.student_status = 'Old'
        if self.grad_status is None:
            pass
        elif self.is_passed():
            self.next_grade_level = self.grad_status.grade_level + int(1)
        elif self.is_failed():
            self.next_grade_level = self.grad_status.grade_level
            self.grad_status.current = False
        return self.next_grade_level


@app.route('/enroll/', methods=['GET', 'POST'])
@login_required
def enroll():
    if not app.config['Enrollment']:
        return render_template('enrollment_unavailable.html')
    form = EnrollmentForm()
    e = EnrollmentLogic()
    if e.grade_status_is_none():
        if e.is_admin():
            flash("You're the admin. The Registration page is intended for students only.")
            return render_template('enrollment_unavailable.html')
        flash("Registration is on going. You can now enroll.")
    if e.is_transferee():
        del form.grade_level
    if form.validate_on_submit():
        if e.grade_trans():
            flash("Please choose your Grade.")
            enrolle = Registration(
                        school_year = app.config['CSY'],
                        stud_id = user.stud_id,
                        grade_level = form.grade_level.data,
                        year_level_status = 'Enrolled'
                        )
            current_user.student_status = 'Old'
            db.session.add(enrolle)
            db.session.commit()
            return redirect(url_for('index'))
        elif e.grade_old():
            if not e.grade_status_is_none():
                if e.is_enrolled():
                    flash('You are already enrolled.')
                if e.is_passed():
                    if e.is_graduate():
                        return render_template('graduate.html')
                    e.grad_status.current = False
                    flash("Congratulations! You've passed your current grade. Your are now enrolled.")
                    db.session.add(e.enrollee)
                    db.session.commit()
                elif e.is_failed():
                    flash('Unfortunately you failed.')
                    db.session.add(e.enrollee)
                    db.session.commit()
        elif e.grade_new():
            flash('You are enrolled in Grade 7')
            enrolle = Registration(
                        school_year = app.config['CSY'],
                        stud_id = e.user.stud_id,
                        grade_level = '7',
                        year_level_status = 'Enrolled'
                        )
            db.session.add(e.user)
            db.session.add(e.enrollee)
            db.session.commit()
    return render_template('enroll.html', form=form)

@app.route('/signup/', methods=['GET', 'POST'])
@logout_required
def signup():
    form = RegisterForm(request.form)
    username = form.username.data
    password = form.password.data,
    student_status = form.student_status.data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username is already taken.')
            return render_template('signup.html', form=form, username=username, password=password, student_status=student_status)
        user = User(
                    username = form.username.data,
                    password = form.password.data,
                    student_status = form.student_status.data,
                    )
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful')
        return redirect(url_for('index'))
    return render_template('signup.html', form=form, username=username, password=password, student_status=student_status)
"""ModelView"""
class UserView(ModelView, BaseView):
    excluded_fields = ['password_hash', 'gender', 'birth_date', 'age', 'birth_place', 'religion', 'present_address', 'email', 'contact_number', 'role']
    page_size = 10
    can_export = True
    can_view_details = True
    column_filters = ['username', 'role', 'student_status']
    column_exclude_list = excluded_fields
    column_export_exclude_list = excluded_fields
    form_choices = {'role': [
        ('Admin', 'Administrator'),
        ('Student', 'Student')
    ]}

#    def is_accessible(self):
#        return current_user.role =='Admin'

#    def inaccessible_callback(self, name, **kwargs):
#        return redirect(url_for('login', next=request.url))

class RegistrationView(ModelView, BaseView):
    page_size = 100
    can_export = True
    column_filters = ['school_year', 'grade_level', 'year_level_status']
    form_choices = {'year_level_status': [
        ('Passed', 'The Student Passed'),
        ('Failed', 'The Student Failed')
    ]}

    def is_accessible(self):
        return current_user.role =='Admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class TeacherView(ModelView, BaseView):
    excluded_fields = ['password_hash', 'gender', 'birth_date', 'age', 'birth_place', 'religion', 'present_address', 'email', 'contact_number', 'role']
    excluded_form_columns = ['password_hash', 'gender', 'birth_date', 'age', 'birth_place', 'religion', 'present_address', 'email', 'contact_number', 'role','student_status', 'username', 'last_name', 'first_name', 'middle_name', 'last_name','authenticated']
    page_size = 10
    can_export = True
    can_create = False
    can_delete = False
    form_excluded_columns = excluded_form_columns
    column_filters = ['username', 'student_status']
    column_exclude_list = excluded_fields
    column_export_exclude_list = excluded_fields
    inline_models = (Registration,)
    can_delete = False
    form_choices = {'role': [
        ('Admin', 'Administrator'),
        ('Student', 'Student'),
        ('Teacher', 'Teacher')
    ]}

    def get_query(self):
        return self.session.query(self.model).filter(self.model.role == 'Student')

    def is_accessible(self):
        return current_user.role == 'Admin' or current_user.role == 'Teacher'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

"""Flask-Admin"""
admin = Admin(app, name='Bnhs', template_mode='bootstrap3', index_view=None)
admin.add_view(UserView(User, db.session, endpoint='user-admin'))
admin.add_view(RegistrationView(Registration, db.session))
admin.add_link(IsnotLoggedinMenuLink(name='Login', endpoint='login'))
admin.add_link(IsAdminMenuLink(name='Logout', endpoint='logout'))
#admin.add_view(TeacherView(User, db.session, endpoint='user'))
"""main program"""
if __name__ == '__main__':
#    db.drop_all()
    db.create_all()
    app.run(debug=True)

