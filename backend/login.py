from req import RequestHandler
from req import Service
from req import reqenv
from mail import MailHandler
import random
import os

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
        self.forget_mail = MailHandler('templ/forget_mail.html')
        LoginService.inst = self

    def signup(self, email, pwd, rpwd):
        if not email or email == '':
            return ('Eemptyemail', None)
        if not pwd or pwd == '':
            return ('Eemptypwd', None)
        if pwd != rpwd:
            return ('Erpwd', None)
        if email.find('@') == -1:
            return ('Enotemail', None)
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
        yield cur.execute('INSERT INTO "account_info" ("uid") VALUES(%s);', (uid,))
        path = os.path.abspath(os.path.join(os.path.dirname("__file__"),os.path.pardir)) + '/http/'
        path += str(uid)
        os.mkdir(path)
        return (None, uid)

    def signin(self, email, pwd):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "uid", "pwd" FROM "account" WHERE "email" = %s;', (email,))
        if cur.rowcount != 1:
            return ('Eemail', None)
        (uid, hpwd) = cur.fetchone()
        if str(_hash(pwd)) != hpwd:
            return ('Epwd', None)
        return (None, int(uid))

    def forget_password(self, email):
        def random_password():
            return str(random.randint(0,100000000000))
        cur = yield self.db.cursor()
        print(email)
        yield cur.execute('SELECT "uid" FROM "account" WHERE "email" = %s;', (email, ))
        print(cur.rowcount)
        if cur.rowcount != 1:
            return ('Eemail', None)
        uid = cur.fetchone()[0]
        npwd = random_password()
        hnpwd = _hash(npwd)
        yield cur.execute('UPDATE "account" SET "pwd" = %s WHERE "uid" = %s;', (hnpwd, uid))
        err = self.forget_mail.send(email, 'change password', email=email, pwd=npwd)
        print('mail',err)
        if err:
            return ('Esendmail', None)
        return (None, uid)

    def change_password(self, acct, data):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "pwd" FROM "account" WHERE "uid" = %s;', (acct['uid'],))
        hpwd = cur.fetchone()[0]
        if str(hpwd) != str(_hash(data['opwd'])):
            return ('Epwd', None)

        if data['npwd'] != data['rnpwd']:
            return ('Enpwd', None)
        yield cur.execute('UPDATE "account" SET "pwd" = %s WHERE "uid" = %s;', (_hash(data['npwd']), acct['uid'], ))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, acct['uid'])


    def get_account_info(self, uid):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "email", "type", "info_confirm", "pay" FROM "account" WHERE "uid" = %s;', (uid,))
        if cur.rowcount != 1:
            return ('Euid', None)
        (email, _type, info_confirm, pay) = cur.fetchone()
        meta = {'uid': uid,
                'email': email,
                'type': _type,
                'info_confirm': info_confirm,
                'pay': int(pay)
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
            err, uid = yield from LoginService.inst.signin(email, pwd)
            if err:
                self.finish(err)
                return
            self.set_secure_cookie('uid', str(uid))
            self.finish('S')
        elif req == 'signup':
            email = self.get_argument('email', None)
            pwd = self.get_argument('pwd', None)
            rpwd = self.get_argument('rpwd', None)
            err, uid = yield from LoginService.inst.signup(email, pwd, rpwd)
            if err:
                self.finish(err)
                return
            self.finish('S')
        elif req == 'forget':
            email = self.get_argument('email', None)
            err, uid = yield from LoginService.inst.forget_password(email)
            if err:
                self.finish(err)
                return
            self.finish('S')
        elif req == 'change':
            args = ['opwd', 'npwd', 'rnpwd']
            meta = self.get_args(args)
            err, uid = yield from LoginService.inst.change_password(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
        return 
