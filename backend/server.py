import tornado.ioloop
import tornado.httpserver
import tornado.web

import pg
import config
from req import RequestHandler
from req import reqenv
from req import Service

from login import LoginHandler
from login import LoginService
from user import UserHandler
from user import UserService
from logout import LogoutHandler
import signal
import time


class IndexHandler(RequestHandler):
    @reqenv
    def get(self):
        islogin = False
        issetdata = False
        acct = "normal"
        if not self.acct:
            self.render("login.html")
        else:
            if acct[0:5] == "admin":
                self.render(acct)
            else:
                if not issetdata:
                    self.render("modify_user.html", nationality=config.id2nationality)
                else:
                    self.render("show_data.html")
        return

    @reqenv
    def post(self):
        return

def sig_handler(sig, frame):
    print('catch stop signal')
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)

def shutdown():
    print('stopping server')
    srv.stop()
    io_loop = tornado.ioloop.IOLoop.instance()
    deadline = time.time() + config.MAX_WAIT_SECOND_BEFORE_SHUTDOWN

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            print('Shutdown')
    stop_loop()


class TestHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('test.html')
        return

if __name__ == '__main__':
    db = pg.AsyncPG(config.DBNAME, config.DBUSER, config.DBPASSWORD, host=config.DBHOST, dbtz='+8')
    app = tornado.web.Application([
        ('/', IndexHandler),
        ('/login', LoginHandler),
        ('/logout', LogoutHandler),
        ('/user', UserHandler),
        ('/test', TestHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': '../http'}),
        ], cookie_secret=config.COOKIE_SECRET, autoescape='xhtml_escape')
    global srv
    srv = tornado.httpserver.HTTPServer(app)
    srv.listen(config.PORT)
    Service.Login = LoginService(db)
    Service.User = UserService(db)
    print('start')
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    tornado.ioloop.IOLoop().instance().start()
