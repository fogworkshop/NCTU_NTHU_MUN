from req import Service
from req import RequestHandler
from req import reqenv

class UserService:
    def __init__(self, db):
        self.db = db
        UserService.inst = self

    def is_info_confirmed(self, acct):
        if not acct:
            return ('Elogin', None)
        pass

    def modify_info(self, acct, data):
        if not acct:
            return ('Elogin', None)
        pass

    def confirm_info(self, acct):
        if not acct:
            return ('Elogin', None)
        uid = int(acct['uid'])
        cur = yield self.db.cursor()

        pass

class UserHandler(RequestHandler):
    @reqenv
    def get(self):
        pass

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'modify_info':
            args = ['chinesename', 'englishname', 'gender', 'birth', 'nationality', 'vegeterian']
            pass
        elif req == 'confirm_info':
            pass
        pass
