from req import Service
from req import RequestHandler
from req import reqenv
import json

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
        if data['englishname'].find(',') != -1 || data['englishname'].find('-') != -1:
            return ('Eenglishname', None)
        if data['cellphone'].isdigit() == False:
            return ('Ecellphone', None)

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
        yield cur.execute('UPDATE "account" SET "info_confirm" = %s WHERE "uid" = %s', (True, uid,))
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
                'residence', 'city', 'address', 'cellphone', 'require_accommodation', 
                'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2', 
                'hearabout', 'experience', 'paycode', 'paydate', 'preference', 'country']
        sql = gen_sql(args)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT '+sql+' FROM "account_info" WHERE "uid" = %s;', (uid, ))
        if cur.rowcount != 1:
            return ('Enoinfo', None)
        q = cur.fetchone()
        meta = {}
        for i, a in enumerate(args):
            meta[a] = q[i]
        meta['hearabout'] = json.loads(meta['hearabout'])
        args = ['email', 'pay', 'info_confirm']
        sql = gen_sql(args)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT '+sql+'FROM "account" WHERE "uid" = %s;', (uid, ))
        if cur.rowcount != 1:
            return ('Enoinfo', None)
        q = cur.fetchone()
        for i, a in enumerate(args):
            meta[a] = q[i]
        return (None, meta)

    def get_info_all(self, acct):
        if not acct:
            return ('Elogin', None)
        if acct['admin'] == 0:
            return ('Eaccess', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "uid" FROM "account" WHERE "email" NOT LIKE \'admin%\' ;')
        uidlist = [ c[0] for c in cur ]
        meta = []
        for uid in uidlist:
            err, submeta = yield from self.get_info(acct, uid)
            if err:
                return (err, None)
            meta.append(submeta)

        meta = sorted(meta, key=lambda m: int(m['uid']))

        return (None, meta)



    def update_pay(self, acct, data):
        if not acct or acct['uid'] != data['uid']:
            return ('Eaccess', None)
        if data['paycode'] == '' or data['paydate'] == '':
            return ('Eempty', None)

        cur = yield self.db.cursor()
        yield cur.execute('SELECT "paycode", "paydate" FROM "account_info" WHERE "uid" = %s;', (data['uid'], ))
        paycode, paydate = cur.fetchone()
        if paycode != '' or paydate == '':
            return ('Efilled', None)

        yield cur.execute('UPDATE "account_info" SET "paycode" = %s, "paydate" = %s WHERE "uid" = %s;', (data['paycode'], data['paydate'], data['uid'], ))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, data['uid'])
       
    def admin_set_pay(self, acct, data):
        if not acct:
            return ('Elogin', None)
        if acct['admin'] == 0:
            return ('Eaccess', None)

        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account" SET "pay" = %s WHERE "uid" = %s;', (data['pay'], data['uid']))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, data['uid'])



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
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2', 'hearabout', 'experience']
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
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2', 'hearabout', 'experience']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.confirm_info(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'update_pay':
            args = ['paycode', 'paydate']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.update_pay(self.acct, data)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'admin_set_pay':
            args = ['pay', 'uid']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.admin_set_pay(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        self.finish('undefined')
