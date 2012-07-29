r = None

#try:
#    from django.conf import STRACKS_API
#except ImportError:
#    STRACKS_API = None

from stracks_api.api import API
from stracksapp.connector import LocalConnector

STRACKS_API = API(LocalConnector())

class StracksMiddleware(object):
    def process_request(self, request):
        global r
        if not STRACKS_API:
            return

        ##
        ## get useragent, ip, path
        ## fetch session, create one if necessary
        ## create request, store it in local thread storage
        useragent = request.META.get('HTTP_USER_AGENT', 'unknown')
        ip = request.META.get('REMOTE_ADDR', '<none>')
        path = request.get_full_path()
        sess = request.session.get('stracks-session')
        if sess is None:
            sess = STRACKS_API.session()
            request.session['stracks-session'] = sess
        request = sess.request(ip, useragent, path)
        r = request ## use LTS
        r.log("Hello World from MiddleWare")

    def process_response(self, request, response):
        global r

        if not STRACKS_API:
            return

        if r is not None:
            r.end()
            r = None
        return response

    def process_exception(self, request, exception):
        ##
        ## fetch request, log exception
        if not STRACKS_API:
            return

