import tornado.ioloop
import tornado.web

import pg
import config
from req import RequestHandler
from req import reqenv
from req import Service

from login import LoginHandler
from login import LoginService


class IndexHandler(RequestHandler):
    @reqenv
    def get(self):
        islogin = False
        issetdata = False
        acct = "normal"
        if not islogin:
            self.render("login.html")
        else:
            if acct[0:5] == "admin":
                self.render(acct)
            else:
                if not issetdata:
                    self.render("modify_user.html")
                else:
                    self.render("show_data.html")
        return

    @reqenv
    def post(self):
        return

if __name__ == '__main__':
    print('start')
    db = pg.AsyncPG(config.DBNAME, config.DBUSER, config.DBPASSWORD, host=config.DBHOST, dbtz='+8')
    app = tornado.web.Application([
        ('/', IndexHandler),
        ('/login', LoginHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': '../http'}),
        ], cookie_secret=config.COOKIE_SECRET, autoescape='xhtml_escape')
    print('app')
    app.listen(config.PORT)
    Service.Login = LoginService(db)
    print('service')
    tornado.ioloop.IOLoop().instance().start()
