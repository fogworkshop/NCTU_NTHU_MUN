from req import RequestHandler
from req import reqenv
from req import Service
import os

class AdminService:
    def __init__(self, db):
        self.db = db
        AdminService.inst = self

    def update_admin3(self, acct, data, flag_img):
        if not acct or acct['admin'] == 0:
            return ('Eaccess', None)

        if not flag_img:
            return ('Eflagimg', None)

        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account_info" SET "represent_country" = %s, "represent_committe" = %s WHERE "uid" = %s;', (data['represent_country'], data['represent_committee'], data['uid'],))
        if cur.rowcount != 1:
            return ('Edb', None)

        filename = flag_img['filename']
        path = os.path.abspath(os.path.join(os.path.dirname("__file__"),os.path.pardir)) + '/http/'
        path += str(data['uid']) + '/flag.' + filename.split('.')[-1]
        f = open(path, 'wb')
        f.write(flag_img['body'])
        f.close()
        return (None, data['uid'])


class AdminHandler(RequestHandler):
    @reqenv
    def get(self):
        pass

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'admin1':
            pass
        elif req == 'admin2':
            pass
        elif req == 'admin3':
            args = ['uid', 'represent_country', 'represent_committee']
            try:
                flag_img = self.request.files['flag'][0]
            except:
                flag_img = None
            meta = self.get_args(args)
            err, uid = yield from AdminService.inst.update_admin1(self.acct, meta, flag_img)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        self.finish('undefined')
        return
