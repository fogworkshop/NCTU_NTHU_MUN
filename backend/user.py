from req import Service
from req import RequestHandler
from req import reqenv
import datetime
import json
import subprocess
import config

class UserService:
    def __init__(self, db):
        self.db = db
        UserService.inst = self

    def is_info_confirmed(self, acct):
        print("is info confirmed")
        if not acct:
            return ('Elogin', None)
        pass

    def modify_info(self, acct, data, check=False):
        print("modify info")
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
        if check:
            if data['englishname'].find(',') != -1 or data['englishname'].find('-') != -1 or data['englishname'] == '':
                return ('Wrong name.', None)
            if data['cellphone'].isdigit() == False:
                return ('You can only type in numbers in the "cellphone" blank.', None)
            if data['committee_preference'].find('0') != -1:
                return ('You must fill in all six preferences.', None)
            cp = json.loads(data['committee_preference'])
            cp = [str(_) for _ in cp]
            if cp.index('4')<3 and cp.index('5')<3 and (data['pc1']=='' or data['pc2']==''):
                return ('Please make sure again that you have filled in all the required information.', None)

        uid = data['uid']
        data.pop('uid')

        if acct['info_confirm']:
            return ('Submitted.', None)

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
            return ('You have to login.', None)

        err, _ = yield from self.modify_info(acct, dict(data), True)
        if err:
            return (err, None)

        uid = data['uid']
        data.pop('uid')

        uid = acct['uid']
        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account" SET "info_confirm" = %s, "submit_time" = %s WHERE "uid" = %s', (True, datetime.datetime.now(), uid,))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, uid)

    def get_info(self, acct, uid):
        print("get_info:", acct)
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
                'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 'iachr2', 'committee', 
                'hearabout', 'experience', 'paycode', 'paydate', 'preference', 'country', 'other', 'ticket', 'id_number', 'emergency_person' ,'emergency_phone']
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
        args = ['email', 'pay', 'info_confirm', 'submit_time']
        sql = gen_sql(args)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT '+sql+'FROM "account" WHERE "uid" = %s;', (uid, ))
        if cur.rowcount != 1:
            return ('Enoinfo', None)
        q = cur.fetchone()
        for i, a in enumerate(args):
            meta[a] = q[i]
        uid = meta['uid']
        sub = subprocess.Popen('find ../http/'+str(uid)+' | grep flag', shell=True, stdout=subprocess.PIPE)
        sub = sub.communicate()[0].decode()
        if sub != '' and sub[-1] == '\n':
            sub = sub[:-1]
        if sub != '':
            meta['flag'] = '/flag.'+sub.split('.')[-1]
        else:
            meta['flag'] = None
        sub = subprocess.Popen('find ../http/'+str(uid)+' | grep guide', shell=True, stdout=subprocess.PIPE)
        sub = sub.communicate()[0].decode()
        if sub != '' and sub[-1] == '\n':
            sub = sub[:-1]
        if sub != '':
            meta['guide'] = '/%d/guide.'%uid+sub.split('.')[-1]
        else:
            meta['guide'] = None
        return (None, meta)

    def get_info_all(self, acct):
        if not acct:
            return ('Elogin', None)
        if acct['admin'] == 0:
            return ('Eaccess', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "uid" FROM "account" WHERE "email" NOT LIKE \'admin%\' ORDER BY "info_confirm" DESC,"submit_time" ASC, "uid" ASC;')
        uidlist = [ c[0] for c in cur ]
        meta = []
        for uid in uidlist:
            err, submeta = yield from self.get_info(acct, uid)
            if err:
                return (err, None)
            meta.append(submeta)

        #meta = sorted(meta, key=lambda m: int(m['uid']))

        return (None, meta)



    def update_pay(self, acct, data):
        if not acct:
            return ('Eaccess', None)
        if data['paycode'] == '' or data['paydate'] == '':
            return ('Eempty', None)

        cur = yield self.db.cursor()
        yield cur.execute('SELECT "paycode", "paydate" FROM "account_info" WHERE "uid" = %s;', (acct['uid'], ))
        paycode, paydate = cur.fetchone()
        if paycode != '' or paydate != '':
            return ('Efilled', None)

        yield cur.execute('UPDATE "account_info" SET "paycode" = %s, "paydate" = %s WHERE "uid" = %s;', (data['paycode'], data['paydate'], acct['uid'], ))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, acct['uid'])

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

    def upload_pp(self, acct, pp):
        if not pp:
            return ('Enofile', None)
        if not acct:
            return ('Elogin', None)
        if not acct['info_confirm']:
            return ('Econfirm', None)
        path = '../http/' + str(acct['uid']) + '/'
        sub = subprocess.Popen('find '+path+' | grep pp' , shell=True, stdout=subprocess.PIPE)
        sub = sub.communicate()[0].decode()
        if sub != '' and sub[-1] == '\n':
            sub = sub[:-1]
        if sub != '':
            subprocess.call('rm '+sub, shell=True)
        filename = pp['filename']
        subname = filename.split('.')[-1]
        f = open(path+'pp.'+subname, 'wb')
        f.write(pp['body'])
        f.close()
        return (None, acct['uid'])

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
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 
                    'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 
                    'iachr2', 'hearabout', 'experience', 'other', 'id_number', 'emergency_person' ,'emergency_phone']
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
                    'residence', 'city', 'address', 'cellphone', 'require_accommodation', 
                    'committee_preference', 'department', 'pc1', 'pc2', 'iachr1', 
                    'iachr2', 'hearabout', 'experience', 'other', 'ticket', 'id_number', 'emergency_person' ,'emergency_phone']
            meta = self.get_args(args)
            meta['ticket'] = '0' if datetime.datetime.now() <= config.EARLYBIRD_DATE else '1'
            err, uid = yield from UserService.inst.confirm_info(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        elif req == 'update_pay':
            args = ['uid', 'paycode', 'paydate']
            meta = self.get_args(args)
            err, uid = yield from UserService.inst.update_pay(self.acct, meta)
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
        elif req == 'upload_pp':
            try:
                pp = self.request.files['pp'][0]
            except:
                pp = None
            err, uid = UserService.inst.upload_pp(self.acct, pp)
            if err:
                self.finish(err)
                return
            self.finish('S')
            return
        self.finish('undefined')
