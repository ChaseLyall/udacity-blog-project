"""Blog Controller

Controls backend functionality of the blog, including:
* create/edit/delete blog posts
* create/edit/delete blog post comments
* like and unlike blog posts

"""

from google.appengine.ext import db

from handler import Handler
from blog_model import *

class BlogHandler(Handler):
    """Generic web handler for the blog"""
    def render_post(self):
        """Render a blog post in HTML"""
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blog-post.html", p=self)

class BlogFront(BlogHandler):
    """Web hanlder for blog front page"""
    def get(self):
        """Get blog front page"""
        posts = Post.all().order('-created')
        out_posts = []
        for post in posts:
            likes = Liked.all().filter(' post_id =', str(post.key().id()))
            out_post = post
            out_post.liked = False
            out_post.like_cnt = 0
            for like in likes:
                out_post.like_cnt += 1
                if self.user and like.author == self.user.name:
                    out_post.liked = True
            out_posts.append(out_post)
        self.render("blog-front.html", posts=out_posts)

class PostPage(BlogHandler):
    """Web hanlder for individual blog post"""
    def get(self, post_id):
        """Get a single blog post"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("404.html")
            return

        comments = Comment.all().filter(' post_id =', post_id).order('created')
        likes = Liked.all().filter(' post_id =', post_id)

        post.liked = False
        post.like_cnt = 0
        for like in likes:
            post.like_cnt += 1
            if self.user and like.author == self.user.name:
                post.liked = True

        self.render("blog-permalink.html", post=post, comments=comments)

class NewPost(BlogHandler):
    """Web hanlder for creating a new blog post"""
    def get(self):
        """Get a web page to create a new blog post"""
        if self.user:
            self.render("blog-newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        """Post (i.e. publish) a new blog post"""
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(parent=blog_key(), author=self.user.name,
                        subject=subject, content=content)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content, please!"
            self.render("blog-newpost.html", subject=subject, content=content, error=error)

class EditPost(BlogHandler):
    """Web handler for editing an existing blog post"""
    def get(self, post_id):
        """Get a web page for editing an existing blog post"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("404.html")
            return

        if self.user and self.user.name == post.author:
            self.render("blog-editpost.html", subject=post.subject, content=post.content, post=post)
        elif self.user and self.user.name != post.author:
            self.redirect("/blog/%s" % str(post_id))
        else:
            self.redirect("/login")

    def post(self, post_id):
        """Post (i.e. publish) a new edit to an existing blog post"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("404.html")
            return

        if not self.user.name == post.author:
            self.redirect("/blog/%s" % str(post_id))

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = "subject and content, please!"
            self.render("blog-editpost.html", subject=subject, content=content,
                        error=error, post=post)

class DeletePost(BlogHandler):
    """Web handler for deleting an existing blog post"""
    def get(self, post_id):
        """Get the webpage in order to delete the blog post"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("404.html")
            return

        if self.user and self.user.name == post.author:
            self.render("blog-deletepost.html", subject=post.subject)
        elif self.user and self.user.name != post.author:
            self.redirect("/blog/%s" % str(post_id))
        else:
            self.redirect("/login")

    def post(self, post_id):
        """Post (i.e. publish) your delete of the blog post"""
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("404.html")
            return

        if not self.user.name == post.author:
            self.redirect("/blog/%s" % str(post_id))

        comments = Comment.all().filter(' post_id =', post_id)
        likes = Liked.all().filter(' post_id =', post_id)

        subject = self.request.get('subject')

        if subject and subject == post.subject:
            post.delete()
            for comment in comments:
                comment.delete()
            for like in likes:
                like.delete()
            self.redirect("/blog")
        elif subject and subject != post.subject:
            error = "Entered subject does not match the post's subject."
            self.render("blog-deletepost.html", subject=post.subject,
                        error=error)
        else:
            error = "Please enter the post's subject to delete this post."
            self.render("blog-deletepost.html", subject=post.subject,
                        error=error)

class Like(BlogHandler):
    """Web hanlder for liking a blog post"""
    def get(self, post_id):
        """Like a blog post"""
        if not self.user:
            self.redirect("/login")
            return

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        liked = Liked.all().filter(' post_id =', str(post_id))
        liked = liked.filter(' author =', self.user.name).get()
        if not liked and post.author != self.user.name:
            liked = Liked(parent=blog_key(), post_id=str(post_id),
                          author=self.user.name)
            liked.put()

        self.redirect("/blog/%s" % str(post_id))

class UnLike(BlogHandler):
    """Web handler for unliking a blog post you previously liked"""
    def get(self, post_id):
        """Unlike a blog post"""
        if not self.user:
            self.redirect("/login")
            return

        liked = Liked.all().filter(' post_id =', str(post_id))
        liked = liked.filter(' author =', self.user.name).get()
        if liked:
            liked.delete()

        self.redirect("/blog/%s" % str(post_id))

class NewComment(BlogHandler):
    """Web hanlder for creating a new comment on an existing blog post"""
    def get(self, post_id):
        """Get a webpage for writing a comment under a blog post"""
        post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(post_key)

        if not post:
            self.render("404.html")
            return

        if self.user:
            self.render("blog-newcomment.html", post=post)
        else:
            self.redirect("/login")

    def post(self, post_id):
        """Post (i.e. publish) a new comment"""
        if not self.user:
            self.redirect('/login')

        post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(post_key)

        if not post:
            self.render("404.html")
            return

        content = self.request.get('content')

        if content:
            comment = Comment(parent=blog_key(), post_id=post_id,
                              author=self.user.name, content=content)
            comment.put()
            self.redirect('/blog/%s' % post_id)
        else:
            error = "Comment cannot be empty"
            self.render("blog-newcomment.html", content=content, post=post,
                        error=error)

class EditComment(BlogHandler):
    """Web handler for editing an existing comment"""
    def get(self, comment_id):
        """Get a web page for editing an existing comment"""
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.render("404.html")
            return

        post_key = db.Key.from_path('Post', int(comment.post_id),
                                    parent=blog_key())
        post = db.get(post_key)

        if self.user and self.user.name == comment.author:
            self.render("blog-editcomment.html", content=comment.content,
                        post=post)
        elif self.user and self.user.name != comment.author:
            self.redirect("/blog/%s" % str(comment.post_id))
        else:
            self.redirect("/login")

    def post(self, comment_id):
        """Post (i.e. publish) an edit to an existing comment"""
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.render("404.html")
            return

        post_key = db.Key.from_path('Post', int(comment.post_id),
                                    parent=blog_key())
        post = db.get(post_key)

        content = self.request.get('content')

        if content:
            comment.content = content
            comment.put()
            self.redirect('/blog/%s' % comment.post_id)
        else:
            error = "Comment cannot be empty"
            self.render("blog-editcomment.html", content=content, post=post,
                        error=error)

class DeleteComment(BlogHandler):
    """Web hanlder for deleting an existing blog post comment"""
    def get(self, comment_id):
        """Get a webpage for deleting an existing blog post comment"""
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.render("404.html")
            return

        post_key = db.Key.from_path('Post', int(comment.post_id),
                                    parent=blog_key())
        post = db.get(post_key)

        if self.user and self.user.name == comment.author:
            self.render("blog-deletecomment.html", content=comment.content,
                        post=post)
        elif self.user and self.user.name != commment.author:
            self.redirect("/blog/%s" % str(comment.post_id))
        else:
            self.redirect("/login")

    def post(self, comment_id):
        """Post (i.e. publish) the deletion of an existng blog post comment"""
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if not comment:
            self.render("404.html")
            return

        post_key = db.Key.from_path('Post', int(comment.post_id),
                                    parent=blog_key())
        post = db.get(post_key)

        if not self.user.name == comment.author:
            self.redirect("/blog/%s" % str(comment.post_id))

        content = self.request.get('content')

        if content and content == comment.content:
            comment.delete()
            self.redirect("/blog/%s" % str(comment.post_id))
        elif content and content != comment.content:
            error = "Entered content does not match the comment's content."
            self.render("blog-deletecomment.html", content=comment.content,
                        post=post, error=error)
        else:
            error = "Please enter the comment's content above to delete this comment."
            self.render("blog-deletecomment.html", content=comment.content,
                        post=post, error=error)
