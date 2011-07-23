__author__ = "intact"
__version__ = "0.1"
__license__ = "BSD"

### CUT HERE (see setup.py)

from beaker.session import SessionObject
from beaker.util import coerce_session_params
from bottle import request, response
from inspect import getargspec


class BottleBeakerSessionObject(SessionObject):
    def flash(self, message, category='message'):
        self.setdefault('_flashes', []).append((category, message))

    def get_flashed_messages(self, with_categories=False):
        if with_categories:
            return self.pop('_flashes', [])
        else:
            return [message[1] for message in self.pop('_flashes', [])]


class BeakerSessionPlugin(object):
    name = 'beakersession'

    def __init__(self, keyword='session', config=None):
        self.config = coerce_session_params(config) if config is not None else {}
        self.keyword = keyword

    def apply(self, callback, context):
        conf = context['config'].get(self.name, {})
        keyword = conf.get('keyword', self.keyword)

        args = getargspec(context['callback'])[0]
        if keyword not in args:
            return callback

        route_config = conf.get('config', None)
        if route_config is None:
            config = self.config
        else:
            config = self.config.copy()
            config.update(coerce_session_params(route_config))

        def wrapper(*args, **kwargs):
            session = BottleBeakerSessionObject(request.environ, **config)
            kwargs[keyword] = session

            try:
                rv = callback(*args, **kwargs)
            finally:
                if session.accessed():
                    session.persist()
                    if session.__dict__['_headers']['set_cookie']:
                        cookie = session.__dict__['_headers']['cookie_out']
                        if cookie:
                            response.set_header('Set-Cookie', cookie.lstrip(), True)
            return rv

        return wrapper

Plugin = BeakerSessionPlugin
