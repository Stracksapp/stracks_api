"""
    Clientside API
"""

import datetime
import random
import json
import sys
import cStringIO
import traceback

from stracks_api import levels
from stracks_api.client import Logger, set_request, exception


try:
    from django.conf import settings
    STRACKS_CONNECTOR = settings.STRACKS_CONNECTOR
except (ImportError, AttributeError):
    STRACKS_CONNECTOR = None
    STRACKS_API = None


class API(object):
    def __init__(self, connector=None):
        self.connector = connector

    def _get_connector(self):
        return self.connector or STRACKS_CONNECTOR

    def session(self, id=None):
        s = Session(self, id)
        c = self._get_connector()
        if c:
            c.send(dict(action='session_start',
                        sessionid=s.id)
                  )
        return s

    def task_context(self, sessionid=None, agent="Task", path="/"):
        s = self.session(sessionid)
        return s.request('0.0.0.0', agent, path)

    def set_owner(self, sessionid, owner):
        c = self._get_connector()
        if c:
            c.send(dict(action="owner",
                        sessionid=sessionid,
                        owner=owner)
                  )
    def send_request(self, session, data):
        """
            Ignore request if it has no (relevant) entries.
        """
        if not data.get('entries'):
            return
        c = self._get_connector()
        if c:
            c.send(dict(action="request",
                        sessionid=session.id,
                        data=data)
                  )

    def session_end(self, session):
        c = self._get_connector()
        if c:
            c.send(dict(action='session_end',
                        sessionid=session.id)
                  )


class Session(object):
    def __init__(self, api, id=None):
        self.api = api
        self.requests = []
        self.id = id or (datetime.datetime.utcnow().strftime("%s.%f") \
                         + str(random.random() * 1000000))

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


class EntityInstance(Logger, dict):
    def __init__(self, *args, **kw):
        super(Entity.instance_class, self).__init__(*args, **kw)
        self.entity = self

class Entity(object):
    instance_class = EntityInstance

    ## allow option to implicitly create
    def __init__(self, id):
        self.entityid = id

    def __call__(self, clientid, name=None):
        return self.instance_class(entity=self.entityid, id=clientid,
                    name=(name or str(clientid)))


class Action(Logger):
    def __init__(self, id):
        self.actionid = id
        self.action = self()

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
        self.owner = None

    def log(self, msg, level=levels.INFO, entities=(), tags=(), action=None,
            exception=None, data=None):
        ## perform some validation on msg and entities
        time = datetime.datetime.utcnow()

        ##
        ## exception can be a simpel truth value in which case the current
        ## exception will be passed, or an actual exception tuple such as
        ## returned by sys.exc_info()

        exc_as_string = None
        if exception:
            if not isinstance(exception, tuple):
                exception = sys.exc_info()
            exc_type, exc_value, exc_tb = exception

            io = cStringIO.StringIO()
            traceback.print_exception(exc_type, exc_value, exc_tb, None, io)
            exc_as_string = io.getvalue()
            io.close()

        if data:
            ##
            ## If data is passed it should be a dict containing the schema
            ## identifier of the data and the data itself. If not, convert it
            ## to such with a default, 'generic' schema.
            ## Schema's help us to nicely format/represent the data
            try:
                data['schema']  ## it might not even be a dict
            except (KeyError, TypeError):
                data = dict(schema='generic', data=data)
            try:
                data = json.dumps(data)
            except (TypeError, ValueError), e:
                data = dict(schema='error', data="Error while encoding data: %s" % str(e))

        if callable(action):
            action = action()

        self.entries.append(
            dict(msg=msg,
                 level=level,
                 entities=entities,
                 tags=tags,
                 action=action,
                 ts=time.isoformat(),
                 exception=exc_as_string,
                 data=data)
        )

    def end(self):
        self.ended = datetime.datetime.utcnow()
        self.session.request_end(self)

    def set_owner(self, owner):
        """ sets the owner for this request. Can be any entity, but it's usually
            a (system) user """
        self.owner = owner

    def data(self):
        ## end time?
        d = dict(ip=self.ip,
                 useragent=self.useragent,
                 path=self.path,
                 started=self.started.isoformat(),
                 ended=self.ended.isoformat(),
                 entries=self.entries,
                 owner=self.owner)
        return d

    def __enter__(self):
        set_request(self)
        return self

    def __exit__(self, type, value, tb):
        if type is not None:
            exception("Crash: %s" % value)
        set_request(None)
        self.end()


class DjangoUser(Entity):
    def __init__(self, id="user/user"):
        super(DjangoUser, self).__init__(id)

    def __call__(self, req_or_user):
        try: ## request?
            user = req_or_user.user
        except AttributeError:
            ## user
            user = req_or_user
        if not user or user.is_anonymous():
            clientid = -1
            name = "Anonymous User"
        else:
            clientid = user.id
            name = user.get_full_name()
            if not name:
                name = user.email

        return super(DjangoUser, self).__call__(clientid, name)

class LogMixin(object):
    @property
    def log(self):
        try:
            logger = self._logger
        except AttributeError:
            logger = self._logger = self.construct_logger()
        return logger

    def construct_logger(self):
        return Logger()
