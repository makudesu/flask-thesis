from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap

kevin = Flask(__name__)
bootstrap = Bootstrap(kevin)

@kevin.route('/')
def index():
    return render_template('index.html')

@kevin.route('/signin')
def signin():
    return render_template('signin.html')

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
    return render_template('index.html')

if __name__ == '__main__':
    kevin.run(debug=True)

