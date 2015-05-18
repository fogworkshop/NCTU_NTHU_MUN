from req import reqenv
from req import RequestHandler

class LogoutHandler(RequestHandler):
    @reqenv
    def get(self):
        self.clear_cookie('uid')
        return
    def post(self):
        self.clear_cookie('uid')
        self.finish('S')
        return 
