from req import RequestHandler
from req import reqenv
from req import Service

from paypal import PaypalPayment
from paypal import PaypalExecute
from paypal import PaypalCheckPayment

class PaymentService:
    def __init__(self, db):
        self.db = db
        PaymentService.inst = self

    def get_url(self, acct):
        if not acct:
            return('Elogin', None)
        if acct['pay'] == 1:
            return('Epaid', None)
        paypal = PaypalPayment()
        _id, url, meta = paypal.create() 
        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account_info" SET "paypalid" = %s WHERE "uid" = %s;', (_id, acct['uid']))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, url)

    def cancel_payment(self, acct):
        if not acct:
            return ('Elogin', None)
        if acct['pay'] == 1:
            return ('Epaid', None)
        cur = yield self.db.cursor()
        yield cur.execute('UPDATE "account_info" SET "paypalid" = \'\' WHERE "uid" = %s;',(acct['uid'],))
        if cur.rowcount != 1:
            return ('Edb', None)
        return (None, acct['uid'])

    def execute_payment(self, acct, data):
        if not acct:
            return ('Elogin', None)
        if acct['pay'] == 1:
            return ('Epaid', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "paypalid" FROM "account_info" WHERE "uid" = %s;', (acct['uid'],))
        _id = cur.fetchone()[0]
        if _id == '':
            return (None, False)
        paypal = PaypalExecute(data['paymentId'], data['PayerID'])
        res = paypal.execute()
        if res:
            yield cur.execute('UPDATE "account" SET "pay" = %s WHERE "uid" = %s;', (1, acct['uid']))
        return (None, res)
        


class PaymentHandler(RequestHandler):
    @reqenv
    def get(self):
        args = ['success', 'cancel', 'paymentId', 'PayerID']
        meta = self.get_args(args)
        if meta['success'] == 'true':
            err, res = yield from PaymentService.inst.execute_payment(self.acct, meta)
            if err:
                self.finish(err)
                return
            self.finish(str(res))
            return
        elif meta['cancel'] == 'true':
            err, uid = yield from PaymentService.inst.cancel_payment(self.acct)
            if err:
                self.finish(err)
                return
            self.finish('you canceled your payment')
            return
        pass

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        if req == 'test':
            err, url = yield from PaymentService.inst.get_url(self.acct)
            if err:
                self.finish(err)
                return
            self.finish(url)
            return
        pass
