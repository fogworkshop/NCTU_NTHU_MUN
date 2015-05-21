from req import RequestHandler
from req import reqenv
from req import Service
import os

class AdminService:
    def __init__(self, db):
        self.db = db
        AdminService.inst = self

    def update_admin1(self, acct, data):
        def gen_sql(data):
            first = True
            sql = ' SET '
            prama = ()
            for i in data:
                if first == False:
                    sql += ','
                first = False
                sql += '"%s" = '%i
                sql += '%s '
                prama = prama + (data[i],)
            return (sql, prama)

        if not acct or acct['admin'] == 0:
            return ('Eaccess', None)

        cur = yield self.db.cursor()
        uid = data['uid']
        data.pop('uid')
        sql, prama = gen_sql(data)
        print('sql', sql)
        print('prama', prama)
        print('uid', uid)
        yield cur.execute('UPDATE "account_info" '+sql+' WHERE "uid" = %s;', prama + (uid,))
        print(cur.rowcount)
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, uid)

    def update_admin2(self, acct, data):
        if not acct or acct['admin'] == 0:
            return ('Eaccess', None)
        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account" SET "pay" = %s WHERE "uid" = %s;', (data['pay'], data['uid']))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, data['uid'])

    def update_admin3(self, acct, data, flag_img):
        def gen_sql(data):
            first = True
            sql = ' SET '
            prama = ()
            for i in data:
                if first == False:
                    sql += ','
                first = False
                sql += '"%s" = '%i
                sql += '%s '
                prama = prama + (data[i],)
            return (sql, prama)
        if not acct or acct['admin'] == 0:
            return ('Eaccess', None)

        if not flag_img:
            return ('Eflagimg', None)

        uid = data['uid']
        data.pop('uid')
        sql, prama = gen_sql(data)
        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account_info" '+sql+' WHERE "uid" = %s;', prama + (uid,))
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
        print(req)
        if req == 'admin1':
            args = ['uid', 'preference', 'country']
            meta = self.get_args(args)
            err, uid = yield from AdminService.inst.update_admin1(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'admin2':
            args = ['uid', 'pay']
            meta = self.get_args(args)
            err, uid = yield from AdminService.inst.update_admin2(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'admin3':
            args = ['uid', 'country', 'committee']
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
