import paypalrestsdk
import config
paypalrestsdk.configure({
    'mode': config.MODE,
    'client_id': config.CLIENT_ID,
    'client_secret': config.CLIENT_SECRET
    })


class PaypalPayment:
    def __init__(self, total=config.TOTAL, currency=config.CURRENCY, 
            description=config.DESCRIPTION):
        self.total = total
        self.currency = currency
        self.description = description
        self.payment = None
        self.payment_url = None
        self._id = None

    def create(self):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": config.RETURN_URL,
                "cancel_url": config.CANCEL_URL},
            "transactions": [{
                "amount": {
                    "total": self.total,
                    "currency": self.currency},
                "description": self.description}]})
        payment.create()
        self.payment = payment
        for i in self.payment['links']:
            if i.method == 'REDIRECT':
                self.payment_url = i.href

        self._id = payment.id
        return self._id, self.payment_url, self.payment.to_dict()


class PaypalExecute:
    def __init__(self, paymentId, PayerID):
        self.payment_id = paymentId
        self.payer_id = PayerID
        self.payment = None

    def execute(self):
        try:
            self.payment = paypalrestsdk.Payment.find(self.payment_id)
        except:
            return "Payment not found"

        return self.payment.execute({"payer_id": self.payer_id})

class PaypalCheckPayment:
    def __init__(self, payment_id=[]):
        self.payment_id = payment_id

    def get(self):
        payment_response = []
        for i in self.payment_id:
            payment_response.append(i.to_dict())
        return payment_response
