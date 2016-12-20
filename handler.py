"""Basic web handler

Provides a basic web handler framework for Google App Engine.
Framework includes the ability to register, login, and logout users.

"""

import hashlib
import hmac
import random
import re
from string import letters

import webapp2
from google.appengine.ext import db

import settings as s

def make_secure_val(val):
    """Creates a secure value for storing in a cookie."""
    return '%s|%s' % (val, hmac.new(s.SECRET, val).hexdigest())

def check_secure_val(secure_val):
    """Reads a secure cookie to make sure the hashed value is equal
    to the input password.
    """
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class Handler(webapp2.RequestHandler):
    """Generic web handler"""
    def write(self, *a, **kw):
        """Write response.out"""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Render Jinja2 template"""
        params['user'] = self.user
        return s.jinja_env.get_template(template).render(params)

    def render(self, template, **kw):
        """Render Jinja2 template"""
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        """Create/write cookie"""
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """Read secure cookie by unhashing it"""
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            return check_secure_val(cookie_val)
        return None

    def initialize(self, *a, **kw):
        """If logged in via cookie, initialize page with user"""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        if uid:
            self.user = user_by_id(int(uid))
        else:
            self.user = None

class NotFoundPageHandler(Handler):
    """404 html page"""
    def get(self):
        """404 get"""
        self.error(404)
        self.render("404.html")

def user_key(group='default'):
    """Get Google Datastore key for users"""
    return db.Key.from_path('users', group)

class User(db.Model):
    """User model for Google Datastore"""
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

def user_by_id(uid):
    """Get user by user_id"""
    return User.get_by_id(uid, parent=user_key())

def user_by_name(name):
    """Get user by name"""
    u = User.all().filter('name =', name).get()
    return u

def user_register(name, pw_hash, email=None):
    """Initialize new user entity for Google Datastore"""
    return User(parent=user_key(),
                name=name,
                pw_hash=pw_hash,
                email=email)

def make_salt(length=5):
    """Create new salt"""
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt=None):
    """Hash input password with given or new salt"""
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_password(name, password, h):
    """Check if input password matches stored password"""
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def valid_username_re(username):
    """Check if input username meets requirements"""
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return username and USER_RE.match(username)

def valid_password_re(password):
    """Check if input password meets requirements"""
    PASS_RE = re.compile(r"^.{3,20}$")
    return password and PASS_RE.match(password)

def valid_email_re(email):
    """Check if input email meets requirements"""
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return not email or EMAIL_RE.match(email)

def verify_login(name, pw):
    """Check user login matches stored password"""
    user = user_by_name(name)
    if user and valid_password(name, pw, user.pw_hash):
        return user

def login(webHandler, user):
    """Login by setting secure cookie with user_id"""
    webHandler.set_secure_cookie('user_id', str(user.key().id()))

class Signup(Handler):
    """Web handler for registering user"""
    def get(self):
        """Signup get"""
        self.render("signup-form.html")

    def post(self):
        """Signup post new user"""
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.pw_verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

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
        """Signup done registering"""
        #make sure the user doesn't already exist
        user = user_by_name(self.username)
        if user:
            msg = "That username already exists."
            self.render('signup-form.html', error_username=msg)
        else:
            self.pw_hash = make_pw_hash(self.username, self.password)
            user = user_register(self.username, self.pw_hash, self.email)
            user.put()

            login(self, user)
            self.redirect('/blog')

class Login(Handler):
    """Web hanlder for login page"""
    def get(self):
        """Login get"""
        self.render('login-form.html')

    def post(self):
        """Login post username and password"""
        username = self.request.get('username')
        password = self.request.get('password')

        user = verify_login(username, password)
        if user:
            login(self, user)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)

class Logout(Handler):
    """Web handler for logout page"""
    def get(self):
        """Logout get"""
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/blog')

class MainPage(Handler):
    """Web handler for main page"""
    def get(self):
        """Main get"""
        self.render("front.html")

class About(Handler):
    """Web hanlder for about page"""
    def get(self):
        """About get"""
        self.render("about.html")
