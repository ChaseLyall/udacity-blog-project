"""Blog model

Creates all data models in Google's Datastore.
Any model kinds necessary for the blog are created below.
"""

from google.appengine.ext import db

import settings as s

def blog_key(name='default'):
    """Grab parent key for blog database"""
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    """Blog post model, for storing posts"""
    author = db.StringProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self, user):
        """Render blog post in HTML using blog-post.html"""
        self._render_text = self.content.replace('\n', '<br>')
        return s.jinja_env.get_template("blog-post.html").render(p=self,
                                                                 user=user)

class Comment(db.Model):
    """Blog post comment model, for storing comments"""
    post_id = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def render(self, user):
        """Render blog post comment in HTML using blog-comment.html"""
        self._render_text = self.content.replace('\n', '<br>')
        return s.jinja_env.get_template("blog-comment.html").render(c=self,
                                                                    user=user)

class Liked(db.Model):
    """Blog post like model, for storing whether someone likes a blog post"""
    post_id = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
