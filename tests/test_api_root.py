# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :

#from webob import Request
from pylons.controllers.util import Request
from paste.registry import Registry
import pylons
import routes

from vigilo.models.session import DBSession
from vigilo.models import tables

from vigilo.turbogears.controllers.api.root import ApiRootController
import utils
import tg

from tg.tests.base import TestWSGIController, make_app, create_request

default_map = routes.Mapper()
## Setup a default route for the error controller:
#default_map.connect('error/:action/:id', controller='error')
## Setup a default route for the root of object dispatch
#default_map.connect('*url', controller='root', action='routes_placeholder')

#class TestApiRoot(utils.ApiTest):
class TestApiRoot(TestWSGIController):
    def __init__(self, *args, **kargs):
        TestWSGIController.__init__(self, *args, **kargs)
        self.environ = {
            'repoze.what.credentials': {
                'groups': ['managers'],
            }
        }
        #request = create_request("/", self.environ)
        #print req, req.__dict__
        request = Request(self.environ)
        registry = Registry()
        registry.prepare()
        #registry.register(tg.request, request)
        registry.register(pylons.url, request)
        #registry.register(routes.url_for, request)
        pylons.url._push_object(routes.URLGenerator(default_map, self.environ))
        self.app = make_app(ApiRootController, self.environ)
        #environ['paste.registry'].register(myglobal, obj)

    def setUp(self):
        super(TestApiRoot, self).setUp()

    def test_root(self):
        #from tg.tests.base import make_app, create_request
        #app = make_app(ApiRootController, environ)
        #print dir(request), request.__dict__
        #print dir(self.app), self.app.__dict__, self.app.app.__dict__
        #print request.GET("/")
        request = create_request("/", self.environ)
        #print self.get_response()
        print pylons.templating.available_engines
        print self.app.get("/")
        self.fail()
        res = self._query_autocompleter('foobarbaz', False)
        expected = {'results': ['foobarbaz']}
        self.assertEqual(res, expected)
        return self.ctrl.host(pattern, partial)

