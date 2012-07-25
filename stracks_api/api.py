"""
    Clientside API
"""

import datetime
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

    def session(self, app):
        return Session(self, app)

    def send(self, data):
        """ send data to the connector """
        self.connector.send(data)

class Session(object):
    def __init__(self, api, app):
        self.api = api
        self.app = app
        self.requests = []

    def request(self, ip, useragent, path):
        r = Request(self, ip, useragent, path)
        self.requests.append(r)
        return r

    def end(self):
        """ session ends, send data to connector """
        data = {'app':self.app, 'requests':[]}
        for r in self.requests:
            data['requests'].append(r.data())
        self.api.send(data)

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

        pass

    def data(self):
        ## end time?
        d = dict(ts=self.time,
                 ip=self.ip,
                 useragent=self.useragent,
                 path=self.path,
                 time=self.time,
                 entries=self.entries)
        return d
