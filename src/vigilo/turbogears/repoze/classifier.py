# -*- coding: utf-8 -*-
# Copyright (C) 2011-2015 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Contient la fonction de classement des requêtes HTTP.

Trois types de requêtes sont actuellement définis:
- "vigilo-api" : pour les requêtes concernant l'API de Vigilo.
- "browser-external" :  pour les requêtes faites par un navigateur HTTP
                        et ayant fait l'objet d'une authentification par
                        un mécanisme externe (ex: Kerberos).
- "browser" :           pour les autres requêtes faites par un navigateur.
"""

import zope.interface
from repoze.who.interfaces import IRequestClassifier
from repoze.who.classifiers import default_request_classifier

def vigilo_classifier(environ):
    from paste.httpheaders import PATH_INFO
    if '/api/' in PATH_INFO(environ):
        return 'vigilo-api'

    # Sinon, on s'en remet au classifier par défaut (qui identifie
    # le type "browser" correspondant à une requête de navigateur HTTP).
    default = default_request_classifier(environ)

    # S'il s'agit d'une requête de navigateur et qu'une authentification
    # externe a été utilisée, on l'indique ici.
    # @TODO:    repoze.who permet de définir une autre clé que REMOTE_USER;
    #           il faudrait réutiliser celle définie via repoze.who.
    if default == 'browser' and environ.get('REMOTE_USER'):
        return 'browser-external'
    return default

zope.interface.directlyProvides(vigilo_classifier, IRequestClassifier)
