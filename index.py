from flask import Flask, render_template, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

kevin = Flask(__name__)
kevin.config['SECRET_KEY'] = '128JSD*idfedf8ued89f7JHEDFjtw1143589123849iU*(UDF*D*F()D*F)(D*fjsdjfkj238490sdjfkjJDJFi(*)(&^&^*%tYYGHGhjBBb*H*hffJghgdfhkjk3eio2u3oiuqwoieuoiqyopolavofuiekghogsjdb*&&&DFOD&*F*(D&F*(DIOFUIKFHJDJHCKJVHJKCVkchvuhyiudyf8s9df98789743124789238UIOuFKAHDFKJAHDKLASHjkdgasgdhhasdgkjashdU(*&(*&*(*^^ASd876a7s6d87&&$^%$^#<F2>3234$#@121432!$25434%79^)*X&D(97_(A*Sd09POJZXd'
Bootstrap(kevin)

class NameForm(Form):
    email = StringField('Email Address', validators=[Required()])
    password = StringField('Password', validators=[Required()])
    submit = SubmitField('Submit')

@kevin.route('/')
def index():
    return render_template('index.html')

@kevin.route('/signin', methods=['GET', 'POST'])
def signin():
    email = None
    password = None
    form = NameForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        form.email.data = ''
        form.password.data = ''
        flash('Success')
    return render_template('signin.html', form=form, email=email, password=password)

@kevin.route('/signup')
def signup():
    return render_template('signup.html')

@kevin.route('/logout')
def logout():
    return render_template('logout.html')

@kevin.route('/enroll')
def enroll():
    return render_template('enroll.html')

@kevin.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    kevin.run(debug=True)

