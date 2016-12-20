import webapp2

from handler import *
from blog import blog_controller

'''URLs'''
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/about', About),
                               ('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/?', blog_controller.BlogFront),
                               ('/blog/([0-9]+)', blog_controller.PostPage),
                               ('/blog/newpost', blog_controller.NewPost),
                               ('/blog/edit-post/([0-9]+)', blog_controller.EditPost),
                               ('/blog/delete-post/([0-9]+)', blog_controller.DeletePost),
                               ('/blog/add-comment/([0-9]+)', blog_controller.NewComment),
                               ('/blog/edit-comment/([0-9]+)', blog_controller.EditComment),
                               ('/blog/delete-comment/([0-9]+)', blog_controller.DeleteComment),
                               ('/blog/like/([0-9]+)', blog_controller.Like),
                               ('/blog/unlike/([0-9]+)', blog_controller.UnLike),
                               ('/.*', NotFoundPageHandler)
                               ],
                              debug=True)