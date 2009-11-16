# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
"""
Definit la classe chargée de gérer la configuration des applications
utilisant Turbogears sur Vigilo.
"""

from pkg_resources import resource_filename
import gettext

from tg.configuration import AppConfig, config
from tg.i18n import get_lang
from tg.render import render_genshi

from genshi.template import TemplateLoader
from genshi.filters import Translator

from vigilo.common.conf import settings
from vigilo.models import User, UserGroup, Permission

__all__ = ('VigiloAppConfig', )

class VigiloAppConfig(AppConfig):
    """On modifie AppConfig selon nos besoins."""

    def __init__(self, app_name):
        """Crée une nouvelle configuration."""
        super(VigiloAppConfig, self).__init__()
        self.__app_name = app_name
        self.__tpl_translator = None

        # Pour gérer les thèmes, la notation "pointée" n'est pas utilisée.
        # À la place, on indique le nom complet du template (ex: "index.html")
        # lors de l'appel au décorateur @expose.
        self.use_dotted_templatenames = False

        # On définit cette variable à False. En réalité, le comportement
        # est le même que si elle valait toujours True, sauf que l'on
        # met en place les middlewares nous même pour pouvoir gérer les
        # thèmes (cf. <module>/config/middleware.py dans une application).
        self.serve_static = False

        # what is the class you want to use to search
        # for users in the database
        self.sa_auth.user_class = User

        # what is the class you want to use to search
        # for groups in the database
        self.sa_auth.group_class = UserGroup

        # what is the class you want to use to search
        # for permissions in the database
        self.sa_auth.permission_class = Permission

        # The name "groups" is already used for groups of hosts.
        # We use "usergroups" when referering to users to avoid confusion.
        self.sa_auth.translations.groups = 'usergroups'

    def __setup_template_translator(self):
        """Crée un traducteur pour les modèles (templates)."""
        if self.__tpl_translator is None:
            i18n_dir = resource_filename('vigilo.themes', 'i18n')

            try:
                # XXX We should make use of fallback languages.
                self.__tpl_translator = gettext.translation(
                    'theme', i18n_dir, get_lang())
            except IOError:
                # During unit tests, no language is defined which results
                # in an error when get_lang() is called.
                # Also, an IOErrpr occurrs when no catalog exists for the
                # given language.
                self.__tpl_translator = gettext.NullTranslations()

    def setup_paths(self):
        """
        Surcharge pour modifier la liste des dossiers dans lesquels Genshi
        va chercher les templates, afin de supporter un système de thèmes.
        """
        super(VigiloAppConfig, self).setup_paths()

        app_templates = resource_filename(
            'vigilo.themes.templates', self.__app_name)
        common_templates = resource_filename(
            'vigilo.themes.templates', 'common')
        self.paths['templates'] = [app_templates, common_templates]

    def setup_genshi_renderer(self):
        """
        Surcharge pour utiliser un traducteur personnalisé dans les
        modèles (templates).
        """
        def template_loaded(template):
            """Appelé lorsqu'un modèle finit son chargement."""
            self.__setup_template_translator()
            template.filters.insert(0, Translator(
                self.__tpl_translator.ugettext))

        def my_render_genshi(template_name, template_vars, **kwargs):
            """Ajoute une fonction l_ dans les modèles pour les traductions."""
            self.__setup_template_translator()

            # Add custom translator to templates.
            template_vars['l_'] = self.__tpl_translator.ugettext
            # Pass Vigilo's settings to templates.
            template_vars['settings'] = settings

            return render_genshi(template_name, template_vars, **kwargs)

        loader = TemplateLoader(search_path=self.paths.templates,
                                auto_reload=self.auto_reload_templates,
                                callback=template_loaded)

        config['pylons.app_globals'].genshi_loader = loader
        self.render_functions.genshi = my_render_genshi

    def setup_sqlalchemy(self):
        """
        Turbogears a besoin de configurer la session de base de données.
        Puis normalement, il appelle la fonction init_model() du modèle
        de l'application avec les paramètres de la session.
        Dans notre cas, la session est déjà configurée globalement (dans
        vigilo.models.session), donc cette étape n'est pas nécessaire.
        On inhibe le comportement de Turbogears ici.
        """
        pass

