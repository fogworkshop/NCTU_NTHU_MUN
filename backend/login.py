from req import RequestHandler
from req import Service
from req import reqenv

def _hash(pwd):
    C = 1048072
    M = 10**9+7
    res = 1029384756
    for _ in pwd:
        res = (C*res+ord(_)) % M
    return res

class LoginService:
    def __init__(self, db):
        self.db = db
        LoginService.inst = self

    def signup(self, email, pwd, rpwd):
        if not email or email == '':
            return ('Eemptyemail', None)
        if not pwd or pwd == '':
            return ('Eemptypwd', None)
        if pwd != rpwd:
            return ('Erpwd', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "uid" FROM "account" WHERE "email" = %s;', (email,))
        if cur.rowcount != 0:
            return ('Eemail', None)
        hpwd = _hash(pwd)
        yield cur.execute('INSERT INTO "account" ("email", "pwd") VALUES(%s, %s) RETURNING "uid";',
                (email, hpwd))
        if cur.rowcount != 1:
            return ('Edb', None)
        uid = int(cur.fetchone()[0])
        return (None, uid)

    def signin(self, email, pwd):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "uid", "pwd" FROM "account" WHERE "email" = %s;', (email))
        if cur.rowcount != 1:
            return ('Eemail', None)
        (uid, hpwd) = cur.fetchone()
        if _hash(pwd) != hpwd:
            return ('Epwd', None)
        return (None, int(uid))

    def get_account_info(self, uid):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "email", "type" FROM "account" WHERE "uid" = %s;', (uid,))
        if cur.rowcount != 1:
            return ('Euid', None)
        (email, _type) = cur.fetchone()
        meta = {'uid': uid,
                'email': email,
                'type': _type
                }
        return (None, meta)

class LoginHandler(RequestHandler):
    @reqenv
    def get(self):
        return

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'signin':
            email = self.get_argument('email', None)
            pwd = self.get_argument('pwd', None)
            rpwd = self.get_argument('rpwd', None)
            err, uid = yield from LoginService.inst.signup(email, pwd, rpwd)
            if err:
                self.finish(err)
            self.finish(str(uid))
        elif req == 'signup':
            email = self.get_argument('email', None)
            pwd = self.get_argument('pwd', None)
            err, uid = yield from LoginService.inst.signin(email, pwd)
            if err:
                self.finish(err)
            self.finish(str(uid))
        return 
