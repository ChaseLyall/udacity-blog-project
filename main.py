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
                               ('/test', Test)
                               ],
                              debug=True)