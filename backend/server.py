import tornado.ioloop
import tornado.web

import pg
import config
from req import RequestHandler
from req import reqenv
from req import Service

class IndexHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('index.html')
        return

    @reqenv
    def post(self):
        return

if __name__ == '__main__':
    app = tornado.web.Application([
        ('/', IndexHandler),
        ], cookie_secret=config.COOKIE_SECRET, autoescape='xhtml_escape')

    app.listen(config.PORT)
    tornado.ioloop.IOLoop().instance().start()
