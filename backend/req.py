import json
import msgpack
import types
import datetime
import collections
import tornado.template
import tornado.gen
import tornado.web
import tornado.websocket

class Service:
    pass

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        try:
            self.get_argument('json')
            self.res_json = True

        except tornado.web.HTTPError:
            self.res_json = False

    def error(self,err):
        self.finish(err)
        return

    def render(self,templ,**kwargs):
        #kwargs['acct'] = self.acct
        class _encoder(json.JSONEncoder):
            def default(self,obj):
                if isinstance(obj,datetime.datetime):
                    return obj.isoformat()

                else:
                    return json.JSONEncoder.default(self,obj)

        def _mp_encoder(obj):
            if isinstance(obj,datetime.datetime):
                return obj.isoformat()
            return obj

        if self.res_json == True:
            self.finish(json.dumps(kwargs,cls = _encoder))

        else:
            tpldr = tornado.template.Loader('./templ')
            data = tpldr.load(templ).generate(**kwargs)
            self.finish(data)

        return

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

def reqenv(func):
    @tornado.gen.coroutine
    def wrap(self,*args,**kwargs):
        try:
            uid = self.get_secure_cookie('uid').decode()
        except:
            uid = '0'
        if uid != '0':
            err, self.acct = yield from Service.Login.get_account_info(str(uid))
        else:
            self.acct = None
        ret = func(self,*args,**kwargs)
        if isinstance(ret,types.GeneratorType):
            ret = yield from ret

        return ret

    return wrap
