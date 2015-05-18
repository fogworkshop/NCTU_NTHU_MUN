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
        if not acct:
            return ('Elogin', None)

        uid = data['uid']
        data.pop('uid')

        if acct['info_confirm']:
            return ('Econfirm', None)
        
        cur = yield self.db.cursor()
        yield cur.execute('SELECT 1 FROM "account_info" WHERE "uid" = %s;', (uid, ))
        if cur.rowcount == 0:
            yield cur.execute('INSERT INTO "account_info" ("uid") VALUES(%s);', (uid,))
        (sql, prama) = gen_sql(data)
        yield cur.execute('UPDATE "account_info" '+sql+' WHERE "uid" = %s;', prama+(uid,))
        
        if cur.rowcount != 1:
            return ('Edb', None)

        return (None, uid)

    def confirm_info(self, acct, data):
        if not acct:
            return ('Elogin', None)

        err, _ = yield from self.modify_info(acct, dict(data))
        if err:
            return (err, None)

        uid = data['uid']
        data.pop('uid')

        uid = acct['uid']
        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account" SET "info_confirm" = %s', (True, ))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, uid)

    def get_info(self, acct, uid):
        def gen_sql(data):
            sql = ' '
            first = True
            for d in data:
                if first == False:
                    sql += ' , '
                first = False
                sql += ' "%s" '%d
            return sql

        if not acct:
            return ('Elogin', None)

        if acct['uid'] != uid and acct['admin'] == 0:
            return ('Eaccess', None)
        args = ['uid', 'chinesename', 'englishname', 'gender', 'birth', 'nationality', 'vegetarian', 
                'university', 'grade', 'delegation', 'delegation_englishname', 'delegation_email', 
                'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2']
        sql = gen_sql(args)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT '+sql+'FROM "account_info" WHERE "uid" = %s;', (uid, ))
        if cur.rowcount != 1:
            return ('Enoinfo', None)
        q = cur.fetchone()
        meta = {}
        for i, a in enumerate(args):
            meta[a] = q[i]
        print(type(meta['chinesename']))
        return (None, meta)


class UserHandler(RequestHandler):
    @reqenv
    def get(self):
        pass

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'modify_info':
            args = ['uid', 'chinesename', 'englishname', 'gender', 'birth', 'nationality', 'vegetarian', 
                    'university', 'grade', 'delegation', 'delegation_englishname', 'delegation_email', 
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.modify_info(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'confirm_info':
            args = ['uid', 'chinesename', 'englishname', 'gender', 'birth', 'nationality', 'vegetarian', 
                    'university', 'grade', 'delegation', 'delegation_englishname', 'delegation_email', 
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.confirm_info(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        self.finish('undefined')
