import hashlib
import hmac
import random
import re
from string import letters

import webapp2
from google.appengine.ext import db

import settings as s

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(s.SECRET, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

'''Generic Handler'''
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return s.jinja_env.get_template(template).render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            return check_secure_val(cookie_val)
        return None

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        if uid:
            self.user = user_by_id(int(uid))
        else:
            self.user = None

class NotFoundPageHandler(Handler):
    def get(self):
        self.error(404)
        self.render("404.html")

'''USER: Model'''
def user_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

'''USER: Controllers'''
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def user_by_id(uid):
    return User.get_by_id(uid, parent = user_key())

def user_by_name(name):
    u = User.all().filter('name =', name).get()
    return u

def user_register(name, pw_hash, email = None):
    return User(parent = user_key(),
                name = name,
                pw_hash = pw_hash,
                email = email)

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_password(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def valid_username_re(username):
    return username and USER_RE.match(username)

def valid_password_re(password):
    return password and PASS_RE.match(password)

def valid_email_re(email):
    return not email or EMAIL_RE.match(email)

def verify_login(name, pw):
    u = user_by_name(name)
    if u and valid_password(name, pw, u.pw_hash):
        return u

def login(webHandler, user):
    webHandler.set_secure_cookie('user_id', str(user.key().id()))

class Signup(Handler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.pw_verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username_re(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password_re(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.pw_verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email_re(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        #make sure the user doesn't already exist
        u = user_by_name(self.username)
        if u:
            msg = "That username already exists."
            self.render('signup-form.html', error_username = msg)
        else:
            self.pw_hash = make_pw_hash(self.username, self.password)
            u = user_register(self.username, self.pw_hash, self.email)
            u.put()

            login(self, u)
            self.redirect('/blog')

class Login(Handler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = verify_login(username, password)
        if u:
            login(self, u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/blog')

class MainPage(Handler):
    def get(self):
        self.render("front.html")

class About(Handler):
    def get(self):
        self.render("about.html")