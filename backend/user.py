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
            sql = ' SET '
            prama = ()
            for i in data:
                sql += '"%s" = '%i
                sql += '%s '
                prama = prama + (data[i],)
            return (sql, prama)
        if not acct:
            return ('Elogin', None)

        if acct['info_confirm']:
            return ('Econfirm', None)
        
        cur = yield self.db.cursor()
        (sql, prama) = gen_sql(data)
        uid = acct['uid']
        yield cur.execute('UPDATE "account_info" '+sql+' WHRER "uid" = %s;', prama+(uid,))
        
        if cur.rowcount != 1:
            return ('Edb', None)

        return (None, uid)

    def confirm_info(self, acct, data):
        if not acct:
            return ('Elogin', None)

        err, _ = yield from self.modify_info(acct, data)
        if err:
            return (err, None)

        uid = acct['uid']
        cur = yield self.db.cursor('UPDATE "account" SET "info_confirm" = %s', (True, ))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, uid)

class UserHandler(RequestHandler):
    @reqenv
    def get(self):
        pass

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'modify_info':
            args = ['chinesename', 'englishname', 'gender', 'birth', 'nationality', 'vegeterian', 
                    'university', 'grade', 'delegation', 'delegation_englishname', 'delegation_email', 
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.modify_info(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'confirm_info':
            args = ['chinesename', 'englishname', 'gender', 'birth', 'nationality', 'vegeterian', 
                    'university', 'grade', 'delegation', 'delegation_englishname', 'delegation_email', 
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 'committee_preference']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.confirm_info(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        self.finish('undefined')
