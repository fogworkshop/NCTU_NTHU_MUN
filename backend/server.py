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
from payment import PaymentHandler
from payment import PaymentService
from admin import AdminHandler
from admin import AdminService
import signal
import datetime
import time


class IndexHandler(RequestHandler):
    @reqenv
    def get(self):
        islogin = False
        issetdata = False
        acct = "normal"
        print('acct',self.acct)
        if not self.acct:
            self.render("login.html")
        else:
            if self.acct['admin'] == 1:
                err, meta = yield from Service.User.get_info_all(self.acct)
                if err:
                    self.finish(err)
                    return
                self.render(self.acct['email']+'.html', meta=meta)
            else:
                err, meta = yield from Service.User.get_info(self.acct, self.acct['uid'])
                if self.acct['info_confirm'] == False:
                    ticket = 0 if datetime.datetime.now() <= config.EARLYBIRD_DATE else 1
                    self.render("modify_user.html", nationality=config.id2nationality, meta=meta, ticket=ticket)
                else:
                    print("goto get_url and acct is:", self.acct)
                    err, url = yield from Service.Payment.get_url(self.acct)
                    if err:
                        self.finish(err)
                        return
                    self.render("show_data.html", meta=meta, payment_url=url)
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
        ('/payment', PaymentHandler),
        ('/test', TestHandler),
        ('/admin', AdminHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': '../http'}),
        ], cookie_secret=config.COOKIE_SECRET, 
        autoescape='xhtml_escape', 
        compress_response = True,
        debug = True)

    global srv
    srv = tornado.httpserver.HTTPServer(app)
    srv.listen(config.PORT)
    Service.Login = LoginService(db)
    Service.User = UserService(db)
    Service.Payment = PaymentService(db)
    Service.Admin = AdminService(db)
    print('start')
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    tornado.ioloop.IOLoop().instance().start()
