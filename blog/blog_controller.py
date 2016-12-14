from google.appengine.ext import db

from handler import Handler
from blog_model import *

'''Blog: Controller'''
class BlogHandler(Handler):
    def render_post(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blog-post.html", p = self)

class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        self.render("blog-front.html", posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("404.html")
            return

        self.render("blog-permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("blog-newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), author = self.user.name, subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("blog-newpost.html", subject=subject, content=content, error=error)