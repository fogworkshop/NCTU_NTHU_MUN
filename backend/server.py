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
        self.render('index.html')
        return

    @reqenv
    def post(self):
        return

if __name__ == '__main__':
    print('start')
    db = pg.AsyncPG(config.DBNAME, config.DBUSER, config.DBPASSWORD, host=config.DBHOST, dbtz='+8')
    app = tornado.web.Application([
        ('/', IndexHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': '../http'}),
        ], cookie_secret=config.COOKIE_SECRET, autoescape='xhtml_escape')
    print('app')
    app.listen(config.PORT)
    Service.Login = LoginService(db)
    print('service')
    tornado.ioloop.IOLoop().instance().start()
