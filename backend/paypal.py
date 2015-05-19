import paypalrestsdk

# ---AUTH---
# IMPORTANT: only use sandbox when testing
# change to live when in production
MODE = 'sandbox'
CLIENT_ID = 'Aci7mxPP9G_VHOAjLlG7kpmT6jD37RxCiVIB5rHbbjWXmUQcLNExfThKdYsqBbkE1iJzyAUM-HxPPEqJ'
CLIENT_SECRET = 'EA2QAS_R3ArMydtN8HhUPaDhMfEIouR7sf1EPWUAirT-YLoT_pzRQWVtpSQ1THUdGGkOg64pQmilajvo'
RETURN_URL = "http://mytwmun.org/payment?success=ture"
CANCEL_URL = "http://mytwmun.org/payment?cancel=ture"
paypalrestsdk.configure({
    'mode': MODE,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
})
# ---Create the payment---
# You can modify 
#   1)total amount of money
#   2)currency
#   3)description of payment, it will show on the payment page
# After create an payment
# return:
#   self.id, self.payment_url, self.payment.to_dict()
#   save "self.id" into user's database
#   show "self.payment_url" to user on page to redirect user to paypal payment page
#   "self.payment.to_dict()" is some meta date for this payment
class Payment:
    def __init__(self, total=1, currency="TWD", description="Payment for mytwmun.org"):
        self.total = total
        self.currency = currency
        self.description = description
        self.payment = None
        self.payment_url = None
        self.id = None

    def create(self):
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": RETURN_URL,
                "cancel_url": CANCEL_URL},
            "transactions": [{
                "amount": {
                    "total": self.total,
                    "currency": self.currency},
                "description": self.description}]})
        self.payment = payment.create()
        for i in self.payment:
            if i.method == 'REDIRECT':
                self.payment_url = i.href
        self.id = payment.id
        return self.id, self.payment_url, self.payment.to_dict()

# ---Execute the payment---
# after payment, user will redirect to RETURN_URL
# get parameter "paymentId" & "PayerID" and execute the payment
# payment will only success after execute it
# return
# "Payment not found": the paymentId is illegal
# False: payment is unpaid
# True: payment is paid

class PayExecute:
    def __init__(self, paymentId, PayerID):
        self.payment_id = paymentId
        self.payer_id = PayerID
        self.payment = None

    def execute(self):
        try:
            self.payment = paypalrestsdk.Payment.find(self.payment_id)
        except:
            return "Payment not found"
        return self.payment.execute({"payer_id": self.payment_id})

# ---Check User Past Payment---
# payment_id: list of user's past payment_id
# it return all the payment data
class CheckPayment:
    def __init__(self, payment_id=[]):
        self.payment_id = payment_id

    def get(self):
        payment_response = []
        for i in self.payment_id:
            payment_response.append(i.to_dict())
        return payment_response
