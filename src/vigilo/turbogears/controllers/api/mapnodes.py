# -*- coding: utf-8 -*-
"""
API d'interrogation des hôtes
"""

import pylons

import tg
from tg import expose, request, validate
from tg.decorators import with_trailing_slash
from tg.controllers import RestController
from tg.exceptions import HTTPNotFound

from vigilo.models import tables
from vigilo.models.session import DBSession

from vigilo.turbogears.controllers.api import get_parent_id


class MapNodesController(RestController):

    @with_trailing_slash
    @expose("api/mapnodes-all.xml",
            content_type="application/vnd.vigilo.api+xml; charset=utf-8")
    @expose("json")
    def get_all(self):
        idmap = get_parent_id("maps")
        if idmap is not None:
            map = DBSession.query(tables.Map).get(idmap)
        else:
            raise HTTPNotFound("The URL seems invalid")
        result = []
        for node in map.nodes:
            result.append({
                "id": node.idmapnode,
                "href": tg.url("/api/maps/%s/nodes/%s" % (idmap, node.idmapnode)),
                })
        return dict(mapnodes=result)


    @expose("api/mapnodes-one.xml",
            content_type="application/vnd.vigilo.api+xml; charset=utf-8")
    @expose("json")
    def get_one(self, idmapnode):
        node = DBSession.query(tables.MapNode).get(idmapnode)
        result = {
                "id": node.idmapnode,
                "label": node.label,
                "x": node.x_pos,
                "y": node.y_pos,
                "widget": node.widget,
                "type": node.type_node,
                "icon": node.icon,
                }
        submaps = []
        for submap in node.submaps:
            submaps.append({
                "id": submap.idmap,
                "href": tg.url("/api/maps/%s" % submap.idmap),
                "title": submap.title,
                })
        result["submaps"] = submaps
        if isinstance(node, tables.MapNodeHost):
            result["host"] = {
                    "id": node.idhost,
                    "href": tg.url("/api/hosts/%s" % node.idhost),
                    }
        elif isinstance(node, tables.MapNodeLls):
            result["lls"] = {
                    "id": node.idservice,
                    "href": tg.url("/api/lls/%s" % node.idservice),
                    }
        elif isinstance(node, tables.MapNodeHls):
            result["hls"] = {
                    "id": node.idservice,
                    "href": tg.url("/api/hls/%s" % node.idservice),
                    }
        return dict(mapnode=result)