"""
    Clientside API
"""

import datetime
import random
from stracks_api import levels

class ConnectorException(Exception):
    pass

class MissingAction(ConnectorException):
    pass

class UnknownAction(ConnectorException):
    pass

class NotImplementedAction(ConnectorException):
    pass

class MissingArgument(ConnectorException):
    pass

class Connector(object):
    """
        Responsible for connecting to the Stracks service.
    """
    def session_start(self, sessionid):
        raise NotImplementedAction("session_start")

    def session_end(self, sessionid):
        raise NotImplementedAction("session_end")

    def request(self, sessionid, requestdata):
        raise NotImplementedAction("request")

    def send(self, data):
        action = data.get('action')
        if action is None:
            raise MissingAction()

        try:
            if action == 'session_start':
                self.session_start(data['sessionid'])
            elif action == 'session_end':
                self.session_end(data['sessionid'])
            elif action == 'request':
                self.request(data['sessionid'], data['data'])
            else:
                raise UnknownAction(action)
        except KeyError, e:
            raise MissingArgument(e.message)


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
                                 sessionid=session.id))


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

    def log(self, msg, level=levels.INFO, entities=(), tags=(), action=None):
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
