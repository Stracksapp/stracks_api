"""
    Clientside API
"""

import datetime
import random
from stracks_api import levels

class Connector(object):
    """
        Responsible for connecting to the Stracks service.
    """
    def send(self, data):
        """ to be implemented """


class HTTPConnector(Connector):
    pass

class RedisConnector(Connector):
    pass

class API(object):
    def __init__(self, connector):
        self.connector = connector

    def session(self):
        s = Session(self)
        self.connector.send(dict(action='session_start',
                                 sessionid=s.id))

        return s

    def send_request(self, session, data):
        self.connector.send(dict(action="request",
                                 sessionid=session.id,
                                 data=data))

    def session_end(self, session):
        self.connector.send(dict(action='session_end',
                                 id=session.id))

class Session(object):
    def __init__(self, api):
        self.api = api
        self.requests = []
        self.id = datetime.datetime.now().strftime("%s.%f") \
                         + str(random.random() * 1000000)

    def request(self, ip, useragent, path):
        r = Request(self, ip, useragent, path)
        self.requests.append(r)
        return r

    def request_end(self, request):
        """ request is complete, send it to connector (through API) """
        data = request.data()
        self.api.send_request(self, data)

    def end(self):
        """ notify that this session has ended """
        ## collect all requests that haven't ended?
        self.api.session_end(self)

class Entity(object):
    ## allow option to implicitly create
    def __init__(self, id):
        self.entityid = id

    def __call__(self, clientid):
        return (self.entityid, clientid)

class Request(object):
    def __init__(self, session, ip, useragent, path):
        self.session = session
        self.ip = ip
        self.useragent = useragent
        self.path = path
        self.time = datetime.datetime.utcnow()
        self.entries = []

    def log(self, msg, level=levels.INFO, entities=None, tags=None, action=None):
        ## perform some validation on msg and entities
        time = datetime.datetime.utcnow()
        self.entries.append(
            dict(msg=msg,
                 level=level,
                 entities=entities,
                 tags=tags,
                 action=action,
                 ts=time)
        )
        # register time
        # setup default IP, useragent, etc entities

    def end(self):
        self.session.request_end(self)

    def data(self):
        ## end time?
        d = dict(ts=self.time,
                 ip=self.ip,
                 useragent=self.useragent,
                 path=self.path,
                 time=self.time,
                 entries=self.entries)
        return d
