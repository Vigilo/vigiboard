# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""
Plugin SHN : High level service
"""

from vigiboard.controllers.vigiboard_plugin import \
        VigiboardRequestPlugin
from vigiboard.model import DBSession, EventsAggregate#, HighLevelService
from pylons.i18n import gettext as _
from tg import tmpl_context, url
from tw.jquery.ui_dialog import JQueryUIDialog

class PluginSHN(VigiboardRequestPlugin):

    """
    Plugin permettant de rajouter le nombre de SHNs impactés à
    l'affichage et d'obtenir une liste détaillée de ces SHNs.
    """

    def __init__(self):
        super(PluginSHN, self).__init__(
            name = _(u'Impacted HLS'),
            style = {'title': _(u'Impacted High-Level Services'),
                'style': 'text-align:center'},
            object_name = "shn"
        )
    
    def show(self, aggregate):
        """Fonction d'affichage"""
        dico = {
            'baseurl': url('/'),
            'idaggregate': aggregate.idaggregate,
            'impacted_hls': len(aggregate.high_level_services),
        }
        # XXX Il faudrait échapper l'URL contenue dans baseurl
        # pour éviter des attaques de type XSS.
        res = ('<a href="javascript:vigiboard_shndialog(' + \
                '\'%(baseurl)s\',\'%(idaggregate)s\')" ' + \
                'class="SHNLien">%(impacted_hls)d</a>') % dico
        return res

    def context(self, context):
        """Fonction de context"""

        # On ajoute 10 espaces insécables pour éviter un bug de JQueryUIDialog:
        # le calcul de la taille de la boîte de dialogue ne tient pas compte
        # de l'espace occupé par la croix permettant de fermer le dialogue.
        # Du coup, elle se retrouve superposée au titre de la boîte.
        tmpl_context.shndialog = JQueryUIDialog(id='SHNDialog',
                autoOpen=False, title='%s%s' % (_(u'High-Level Service'),
                '&#160;' * 10))
        context.append([tmpl_context.shndialog, self.object_name])

    def controller(self, *argv, **krgv):
        """Ajout de fonctionnalités au contrôleur"""
        idaggregate = krgv['idaggregate']
        aggregate = DBSession.query(EventsAggregate) \
                .filter(EventsAggregate.idaggregate == idaggregate).one()
        shns = aggregate.high_level_services

        return dict(shns=[shn.servicename for shn in shns]) 

