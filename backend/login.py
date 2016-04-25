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
        res = yield from self.db.execute('SELECT "uid" FROM "account" WHERE "email" = %s;', (email,))
        if res.rowcount != 0:
            return ('Eemail', None)
        hpwd = _hash(pwd)
        yield from self.db.execute('INSERT INTO "account" ("email", "pwd") VALUES(%s, %s) RETURNING "uid";',
                (email, hpwd))
        if res.rowcount != 1:
            return ('Edb', None)
        uid = int(res.fetchone()[0])
        yield self.db..execute('INSERT INTO "account_info" ("uid") VALUES(%s);', (uid,))
        path = os.path.abspath(os.path.join(os.path.dirname("__file__"),os.path.pardir)) + '/http/'
        path += str(uid)
        os.mkdir(path)
        return (None, uid)

    def signin(self, email, pwd):
        res = yield from self.db.execute('SELECT "uid", "pwd" FROM "account" WHERE "email" = %s;', (email,))
        if res.rowcount != 1:
            return ('Eemail', None)
        (uid, hpwd) = res.fetchone()
        if str(_hash(pwd)) != hpwd:
            return ('Epwd', None)
        return (None, int(uid))

    def forget_password(self, email):
        def random_password():
            return str(random.randint(0,100000000000))
        yield from self.db.execute('SELECT "uid" FROM "account" WHERE "email" = %s;', (email, ))
        if res.rowcount != 1:
            return ('Eemail', None)
        uid = res.fetchone()[0]
        npwd = random_password()
        hnpwd = _hash(npwd)
        yield from self.db.execute('UPDATE "account" SET "pwd" = %s WHERE "uid" = %s;', (hnpwd, uid))
        err = self.forget_mail.send(email, 'change password', email=email, pwd=npwd)
        if err:
            return ('Esendmail', None)
        return (None, uid)

    def change_password(self, acct, data):
        res = yield from self.db.execute('SELECT "pwd" FROM "account" WHERE "uid" = %s;', (acct['uid'],))
        hpwd = res.fetchone()[0]
        if str(hpwd) != str(_hash(data['opwd'])):
            return ('Password Error!', None)

        if data['npwd'] != data['rnpwd']:
            return ('Confirm Password Error!', None)
        res = yield from self.db.execute('UPDATE "account" SET "pwd" = %s WHERE "uid" = %s;', (_hash(data['npwd']), acct['uid'], ))
        if res.rowcount != 1:
            return ('Edb', None)
        return (None, acct['uid'])


    def get_account_info(self, uid):
        res = yield from self.db.execute('SELECT "email", "info_confirm", "pay" FROM "account" WHERE "uid" = %s;', (uid,))
        if res.rowcount != 1:
            return ('Euid', None)
        (email, info_confirm, pay) = res.fetchone()
        meta = {'uid': uid,
                'email': email,
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
            self.finish('Password changed successfully')
        return 
