from req import RequestHandler
from req import reqenv
from req import Service

class AdminService:
    def __init__(self, db):
        self.db = db
        AdminService.inst = self

    def update_admin1(self, acct, data, flag_img):
        if not acct or acct['admin'] == 0:
            return ('Eaccess', None)

        if not flag_img:
            return ('Eflag', None)
        pass


class AdminHandler(RequestHandler):
    @reqenv
    def get(self):
        pass

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'admin1':
            args = ['uid', 'represent_country', 'represent_committee']
            flag_img = self.request.files['flag'][0]
            meta = self.get_args(args)
            pass
        elif req == 'admin2':
            pass
        elif req == 'admin3':
            pass
        self.finish('undefined')
        return
