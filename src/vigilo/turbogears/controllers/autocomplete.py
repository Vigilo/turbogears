# -*- coding: utf-8 -*-
"""
Module permettant de mettre en commun le contrôleur d'auto-complétion
entre les différentes applications de Vigilo.
"""
from tg import expose, request
from sqlalchemy.sql.expression import or_
from repoze.what.predicates import in_group

from vigilo.models.tables import Host, SupItemGroup, LowLevelService, User
from vigilo.models.session import DBSession
from vigilo.models.functions import sql_escape_like
from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE

from vigilo.turbogears.helpers import get_current_user
from vigilo.turbogears.controllers import BaseController

# pylint: disable-msg=R0201,W0232
# - R0201: méthodes pouvant être écrites comme fonctions (imposé par TG2)
# - W0232: absence de __init__ dans la classe (imposé par TG2)

class AutoCompleteController(BaseController):
    """Contrôleur d'auto-complétion."""

    @expose('json')
    def host(self, host):
        """
        Auto-compléteur pour les noms d'hôtes.
        
        @param host: Motif qui doit apparaître dans le nom de l'hôte.
        @type host: C{unicode}
        @note: Les caractères '?' et '*' peuvent être utilisés dans
            le paramètre L{host} pour remplacer un caractère quelconque
            ou une chaîne de caractères, respectivement.
            Ex: 'ho?t*' permet de récupérer 'host', 'honte' et 'hostile',
            mais pas 'hote' ou 'hopital'.
        @return: Un dictionnaire dont la clé 'results' contient la liste
            des noms d'hôtes correspondant au motif donné en entrée
            et auxquels l'utilisateur a accès.
        @rtype: C{dict}
        """
        host = sql_escape_like(host)
        user = get_current_user()
        if not user:
            return dict(results=[])

        hostgroup = SUPITEM_GROUP_TABLE.alias()
        servicegroup = SUPITEM_GROUP_TABLE.alias()
        hostnames = DBSession.query(
                Host.name
            ).distinct(
            ).outerjoin(
                (hostgroup, hostgroup.c.idsupitem == Host.idhost),
                (LowLevelService, LowLevelService.idhost == Host.idhost),
                (servicegroup, servicegroup.c.idsupitem == \
                    LowLevelService.idservice),
            ).filter(Host.name.ilike('%' + host + '%'))

        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            user_groups = user.supitemgroups(False)
            hostnames = hostnames.filter(or_(
                hostgroup.c.idgroup.in_(user_groups),
                servicegroup.c.idgroup.in_(user_groups),
            ))

        hostnames = hostnames.all()
        return dict(results=[h[0] for h in hostnames])

    @expose('json')
    def service(self, service, host=None):
        """
        Auto-compléteur pour les noms des services d'un hôte.
        
        @param host: Nom d'hôte (optionnel) sur lequel s'applique
            l'autocomplétion.
        @type host: C{unicode}
        @param service: Motif qui doit apparaître dans le nom de service.
        @type service: C{unicode}
        @note: Les caractères '?' et '*' peuvent être utilisés dans
            le paramètre L{service} pour remplacer un caractère quelconque
            ou une chaîne de caractères, respectivement.
            Ex: 'ho?t*' permet de récupérer 'host', 'honte' et 'hostile',
            mais pas 'hote' ou 'hopital'.
        @return: Un dictionnaire dont la clé 'results' contient la liste
            des noms de services configurés sur L{host} (ou sur n'importe
            quel hôte si L{host} vaut None), correspondant au motif donné
            et auxquels l'utilisateur a accès.
        @rtype: C{dict}
        """
        service = sql_escape_like(service)
        user = get_current_user()
        if not user:
            return dict(results=[])

        hostgroup = SUPITEM_GROUP_TABLE.alias()
        servicegroup = SUPITEM_GROUP_TABLE.alias()
        services = DBSession.query(
                LowLevelService.servicename
            ).distinct(
            ).outerjoin(
                (Host, Host.idhost == LowLevelService.idhost),
                (hostgroup, hostgroup.c.idsupitem == Host.idhost),
                (servicegroup, servicegroup.c.idsupitem == \
                    LowLevelService.idservice),
            ).filter(LowLevelService.servicename.ilike('%' + service + '%'))

        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            user_groups = user.supitemgroups(False)
            services = services.filter(or_(
                hostgroup.c.idgroup.in_(user_groups),
                servicegroup.c.idgroup.in_(user_groups),
            ))

        if host:
            services = services.filter(Host.name == host)

        services = services.all()
        return dict(results=[s[0] for s in services])

    @expose('json')
    def supitemgroup(self, supitemgroup):
        """
        Auto-compléteur pour les noms des groupes d'éléments supervisés.

        @param supitemgroup: Motif qui doit apparaître dans le nom
            du groupe d'éléments supervisés.
        @type supitemgroup: C{unicode}
        @return: Un dictionnaire dont la clé 'results' contient la liste
            des noms de groupes d'élements supervisés correspondant
            au motif donné et auxquels l'utilisateur a accès.
        @rtype: C{dict}
        """
        supitemgroup = sql_escape_like(supitemgroup)
        user = get_current_user()
        if not user:
            return dict(results=[])

        supitemgroups = DBSession.query(
                SupItemGroup.name
            ).distinct(
            ).filter(SupItemGroup.name.ilike('%' + supitemgroup + '%'))

        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            user_groups = user.supitemgroups(False)
            supitemgroups = supitemgroups.filter(
                SupItemGroup.idgroup.in_(user_groups),
            )

        supitemgroups = supitemgroups.all()
        return dict(results=[s[0] for s in supitemgroups])

