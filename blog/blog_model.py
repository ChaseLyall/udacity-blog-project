from google.appengine.ext import db

import settings as s

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    author = db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self, user):
        self._render_text = self.content.replace('\n', '<br>')
        return s.jinja_env.get_template("blog-post.html").render(p = self, user = user)

class Comment(db.Model):
    post_id = db.StringProperty(required = True)
    author = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self, user):
        self._render_text = self.content.replace('\n', '<br>')
        return s.jinja_env.get_template("blog-comment.html").render(c = self, user = user)

class Liked(db.Model):
    post_id = db.StringProperty(required = True)
    author = db.StringProperty(required = True)