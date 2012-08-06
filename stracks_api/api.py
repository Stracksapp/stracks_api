"""
    Clientside API
"""

import datetime
import random
import requests
import json

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
        """
            Do we need the send() intermediate call?
            Why not just invoke the relevant methods directly?
        """
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
    """
        Connect to the API synchronously through HTTP
    """
    def __init__(self, url):
        """
            A HTTP connector takes the url of the API / AppInstance as
            argument
        """
        self.url = url
        self.queue = []

    def session_start(self, sessionid):
        data = {}
        data['started'] = datetime.datetime.utcnow().isoformat()
        data['sessionid'] = sessionid
        self.queue.append({'action':'start', 'data':data})
        self.flush()

    def session_end(self, sessionid):
        data = {}
        data['ended'] = datetime.datetime.utcnow().isoformat()
        data['sessionid'] = sessionid
        self.queue.append({'action':'end', 'data':data})
        self.flush()

    def request(self, sessionid, requestdata):
        data = {}
        data['sessionid'] = sessionid
        data['requestdata'] = requestdata
        self.queue.append({'action':'request', 'data':data})
        self.flush()

    def flush(self):
        if self.queue:
            requests.post(self.url + "/", data=json.dumps(self.queue))
            self.queue = []


class RedisConnector(Connector):
    """
        A connector that simply stores data in redis (or any other keystore?),
        where a separate task is responsible for sending the data to the 
        Stracks API
    """


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
        self.id = datetime.datetime.utcnow().strftime("%s.%f") \
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

    def __call__(self, clientid, name=None):
        return dict(entity=self.entityid, id=clientid, name=name)


class Action(object):
    def __init__(self, id):
        self.actionid = id

    def __call__(self):
        return dict(action=self.actionid)


class Request(object):
    def __init__(self, session, ip, useragent, path):
        self.session = session
        self.ip = ip
        self.useragent = useragent
        self.path = path
        self.started = datetime.datetime.utcnow()
        self.ended = None
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
                 ts=time.isoformat())
        )

    def end(self):
        self.ended = datetime.datetime.utcnow()
        self.session.request_end(self)

    def data(self):
        ## end time?
        d = dict(ip=self.ip,
                 useragent=self.useragent,
                 path=self.path,
                 started=self.started.isoformat(),
                 ended=self.ended.isoformat(),
                 entries=self.entries)
        return d
