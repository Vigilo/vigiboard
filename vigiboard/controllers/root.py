# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Vigiboard Controller"""

from tg import expose, validate, require, flash, \
    tmpl_context, request, config, session, redirect, url
from tw.forms import validators
from pylons.i18n import ugettext as _
from pylons.i18n import lazy_ugettext as l_
from pylons.controllers.util import abort
from sqlalchemy import not_, and_, asc
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from datetime import datetime
from time import mktime
import math
import urllib

from vigiboard.model import DBSession
from vigiboard.model import Event, EventHistory, CorrEvent, \
                            Host, HostGroup, ServiceGroup, \
                            StateName, User, ServiceLowLevel
from repoze.what.predicates import Any, not_anonymous
from vigiboard.widgets.edit_event import edit_event_status_options
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_controller import VigiboardRootController
from vigilo.turbogears.controllers.autocomplete import AutoCompleteController
from vigilo.models.functions import sql_escape_like
from vigilo.models.secondary_tables import HOST_GROUP_TABLE, \
                                            SERVICE_GROUP_TABLE
from vigiboard.lib.base import BaseController

__all__ = ('RootController', 'get_last_modification_timestamp', 
           'date_to_timestamp')

class RootController(VigiboardRootController):
    """
    Le controller général de vigiboard
    """
    autocomplete = AutoCompleteController(BaseController)

    def process_form_errors(self, *argv, **kwargv):
        """
        Gestion des erreurs de validation : On affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        if request.environ.get('HTTP_REFERER') :
            redirect(request.environ.get('HTTP_REFERER'
                ).split(request.environ.get('HTTP_HOST'))[1])
        else :
            redirect('/')

    @expose('vigiboard.html')
    @require(Any(not_anonymous(), msg=l_("You need to be authenticated")))
    def default(self, page=None, hostgroup=None, servicegroup=None,
            host=None, service=None, output=None, trouble_ticket=None,
            from_date=None, to_date=None, *argv, **krgv):
            
        """
        Page d'accueil de Vigiboard. Elle affiche, suivant la page demandée
        (page 1 par defaut), la liste des événements, rangés par ordre de prise
        en compte, puis de sévérité.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param page: Numéro de la page souhaitée, commence à 1
        @param host: Si l'utilisateur souhaite sélectionner seulement certains
                     événements suivant leur hôte, il peut placer une expression
                     ici en suivant la structure du LIKE en SQL
        @param service: Idem que host mais sur les services
        @param output: Idem que host mais sur le text explicatif
        @param trouble_ticket: Idem que host mais sur les tickets attribués
        """
        if page is None:
            page = 1

        try:
            page = int(page)
        except ValueError:
            abort(404)

        if page < 1:
            page = 1

        username = request.environ['repoze.who.identity']['repoze.who.userid']
        user = User.by_user_name(username)
        
        aggregates = VigiboardRequest(user)
        
        search = {
            'host': '',
            'service': '',
            'output': '',
            'tt': '',
            'from_date': '',
            'to_date': '',
            'hostgroup': '',
            'servicegroup': '',
        }

        # Application des filtres si nécessaire
        if hostgroup:
            search['hostgroup'] = hostgroup
            hostgroup = sql_escape_like(hostgroup)
            hg_alias = aliased(HostGroup)
            aggregates.add_outer_join((hg_alias, hg_alias.idgroup == \
                HOST_GROUP_TABLE.c.idgroup))
            aggregates.add_filter(hg_alias.name.ilike('%%%s%%' % hostgroup))

        if servicegroup:
            search['servicegroup'] = servicegroup
            servicegroup = sql_escape_like(servicegroup)
            sg_alias = aliased(ServiceGroup)
            aggregates.add_outer_join((sg_alias, sg_alias.idgroup == \
                SERVICE_GROUP_TABLE.c.idgroup))
            aggregates.add_filter(sg_alias.name.ilike(
                '%%%s%%' % servicegroup))

        if host:
            search['host'] = host
            host = sql_escape_like(host)
            aggregates.add_filter(Host.name.ilike('%%%s%%' % host))

        if service:
            search['service'] = service
            service = sql_escape_like(service)
            aggregates.add_filter(ServiceLowLevel.servicename.ilike(
                '%%%s%%' % service))

        if output:
            search['output'] = output
            output = sql_escape_like(output)
            aggregates.add_filter(Event.message.ilike('%%%s%%' % output))

        if trouble_ticket:
            search['tt'] = trouble_ticket
            trouble_ticket = sql_escape_like(trouble_ticket)
            aggregates.add_filter(CorrEvent.trouble_ticket.ilike(
                '%%%s%%' % trouble_ticket))

        if from_date:
            search['from_date'] = from_date
            # TRANSLATORS: Format de date et heure.
            try:
                from_date = datetime.strptime(
                    from_date, _('%Y-%m-%d %I:%M:%S %p'))
            except ValueError:
                to_date = None
            aggregates.add_filter(CorrEvent.timestamp_active >= from_date)

        if to_date:
            search['to_date'] = to_date
            # TRANSLATORS: Format de date et heure.
            try:
                to_date = datetime.strptime(
                    to_date, _('%Y-%m-%d %I:%M:%S %p'))
            except ValueError:
                to_date = None
            aggregates.add_filter(CorrEvent.timestamp_active <= to_date)

        # Calcul des éléments à afficher et du nombre de pages possibles
        total_rows = aggregates.num_rows()
        items_per_page = int(config['vigiboard_items_per_page'])

        id_first_row = items_per_page * (page-1)
        id_last_row = min(id_first_row + items_per_page, total_rows)

        aggregates.format_events(id_first_row, id_last_row)
        aggregates.generate_tmpl_context()

        nb_pages = int(math.ceil(total_rows / (items_per_page + 0.0)))
        if not total_rows:
            id_first_row = 0
        else:
            id_first_row += 1

        return dict(
            events = aggregates.events,
            rows_info = {
                'id_first_row': id_first_row,
                'id_last_row': id_last_row,
                'total_rows': total_rows,
            },
            nb_pages = nb_pages,
            page = page,
            event_edit_status_options = edit_event_status_options,
            history = [],
            hist_error = False,
            plugin_context = aggregates.context_fct,
            search = search,
            refresh_times = config['vigiboard_refresh_times'],
        )
      
    @validate(validators={'idcorrevent': validators.Int(not_empty=True)},
            error_handler=process_form_errors)
    @expose('json')
    @require(Any(not_anonymous(), msg=l_("You need to be authenticated")))
    def history_dialog(self, idcorrevent):
        
        """
        JSon renvoyant les éléments pour l'affichage de la fenêtre de dialogue
        contenant des liens internes et externes.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param id: identifiant de l'événement
        """

        # Obtention de données sur l'événement et sur son historique
        username = request.environ.get('repoze.who.identity'
                    ).get('repoze.who.userid')
        user = User.by_user_name(username)
        user_groups = user.groups

#        try:
        event = DBSession.query(
                        CorrEvent.priority,
                        Event,
                 ).join(
                    (Event, CorrEvent.idcause == Event.idevent),
                    (ServiceLowLevel, Event.idsupitem == ServiceLowLevel.idservice),
                    (Host, Host.idhost == ServiceLowLevel.idhost),
                    (HOST_GROUP_TABLE, HOST_GROUP_TABLE.c.idhost == Host.idhost),
                    (SERVICE_GROUP_TABLE, SERVICE_GROUP_TABLE.c.idservice == \
                        ServiceLowLevel.idservice),
                 ).filter(HOST_GROUP_TABLE.c.idgroup.in_(user_groups)
                 ).filter(SERVICE_GROUP_TABLE.c.idgroup.in_(user_groups)
                 ).filter(
                    # On masque les événements avec l'état OK
                    # et traités (status == u'AAClosed').
                    not_(and_(
                        StateName.statename == u'OK',
                        CorrEvent.status == u'AAClosed'
                    ))
                ).filter(CorrEvent.idcorrevent == idcorrevent
                ).one()
#        except:
#            # XXX Raise some HTTP error.
#            return None

        history = DBSession.query(
                    EventHistory,
                 ).filter(EventHistory.idevent == event[1].idevent
                 ).order_by(asc(EventHistory.timestamp)
                 ).order_by(asc(EventHistory.type_action)).all()

        eventdetails = {}
        for edname, edlink in \
                config['vigiboard_links.eventdetails'].iteritems():

            # Rappel:
            # event[0] = priorité de l'alerte corrélée.
            # event[1] = alerte brute.
            eventdetails[edname] = edlink[1] % {
                'idcorrevent': idcorrevent,
                'host': urllib.quote(event[1].supitem.host.name),
                'service': urllib.quote(event[1].supitem.servicename),
                'message': urllib.quote(event[1].message),
            }

        return dict(
                current_state = StateName.value_to_statename(
                                    event[1].current_state),
                initial_state = StateName.value_to_statename(
                                    event[1].initial_state),
                peak_state = StateName.value_to_statename(
                                    event[1].peak_state),
                idcorrevent = idcorrevent,
                host = event[1].supitem.host.name,
                service = event[1].supitem.servicename,
                eventdetails = eventdetails,
            )

    @validate(validators={'idcorrevent': validators.Int(not_empty=True)},
            error_handler=process_form_errors)
    @expose('vigiboard.html')
    @require(Any(not_anonymous(), msg=l_("You need to be authenticated")))
    def event(self, idcorrevent):
        """
        Affichage de l'historique d'un événement.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param idevent: identifiant de l'événement souhaité
        """

        username = request.environ['repoze.who.identity']['repoze.who.userid']
        events = VigiboardRequest(User.by_user_name(username))
        events.add_filter(CorrEvent.idcorrevent == idcorrevent)
        
        # Vérification que l'événement existe
        if events.num_rows() != 1 :
            flash(_('Error in DB'), 'error')
            redirect('/')
       
        events.format_events(0, 1)
        events.format_history()
        events.generate_tmpl_context() 

        return dict(
                    events = events.events,
                    rows_info = {
                        'id_first_row': 1,
                        'id_last_row': 1,
                        'total_rows': 1,
                    },
                    nb_pages = 1,
                    page = 1,
                    event_edit_status_options = edit_event_status_options,
                    history = events.hist,
                    hist_error = True,
                    plugin_context = events.context_fct,
                    search = {
                        'host': None,
                        'service': None,
                        'output': None,
                        'tt': None,
                        'from_date': None,
                        'to_date': None,
                        'hostgroup': None,
                        'servicegroup': None,
                    },
                   refresh_times=config['vigiboard_refresh_times'],
                )

    @validate(validators={'host': validators.NotEmpty(),
        'service': validators.NotEmpty()}, error_handler=process_form_errors)
    @expose('vigiboard.html')
    @require(Any(not_anonymous(), msg=l_("You need to be authenticated")))
    def host_service(self, host, service):
        
        """
        Affichage de l'historique de l'ensemble des événements correspondant
        au host et service demandé.
        Pour accéder à cette page, l'utilisateur doit être authentifié.

        @param host: Nom de l'hôte souhaité.
        @param service: Nom du service souhaité
        """

        username = request.environ['repoze.who.identity']['repoze.who.userid']
        events = VigiboardRequest(User.by_user_name(username))
        events.add_join((ServiceLowLevel, ServiceLowLevel.idservice == Event.idsupitem))
        events.add_join((Host, ServiceLowLevel.idhost == Host.idhost))
        events.add_filter(Host.name == host,
                ServiceLowLevel.servicename == service)

        # XXX On devrait avoir une autre API que ça !!!
        # Supprime le filtre qui empêche d'obtenir des événements fermés
        # (ie: ayant l'état Nagios 'OK' et le statut 'AAClosed').
        if len(events.filter) > 2:
            del events.filter[2]

        # Vérification qu'il y a au moins 1 événement qui correspond
        if events.num_rows() == 0 :
            redirect('/')

        events.format_events(0, events.num_rows())
        events.format_history()
        events.generate_tmpl_context()

        return dict(
                    events = events.events,
                    rows_info = {
                        'id_first_row': 1,
                        'id_last_row': 1,
                        'total_rows': 1,
                    },
                    nb_pages = 1,
                    page = 1,
                    event_edit_status_options = edit_event_status_options,
                    history = events.hist,
                    hist_error = True,
                    plugin_context = events.context_fct,
                    search = {
                        'host': None,
                        'service': None,
                        'output': None,
                        'tt': None,
                        'from_date': None,
                        'to_date': None,
                        'hostgroup': None,
                        'servicegroup': None,
                    },
                    refresh_times=config['vigiboard_refresh_times'],
                )

    @validate(validators={
        "id":validators.Regex(r'^[^,]+(,[^,]*)*,?$'),
#        "trouble_ticket":validators.Regex(r'^[0-9]*$'),
        "status": validators.OneOf([
            'NoChange',
            'None',
            'Acknowledged',
            'AAClosed'
        ])}, error_handler=process_form_errors)
    @require(Any(not_anonymous(), msg=l_("You need to be authenticated")))
    def update(self,**krgv):
        
        """
        Mise à jour d'un événement suivant les arguments passés.
        Cela peut être un changement de ticket ou un changement de statut.
        
        @param krgv['id']: Le ou les identifiants des événements à traiter
        @param krgv['last_modification']: La date de la dernière modification
        dont l'utilisateur est au courant.
        @param krgv['tt']: Nouveau numéro du ticket associé.
        @param krgv['status']: Nouveau status de/des événements.
        """

        # On vérifie que des identifiants ont bien été transmis via
        # le formulaire, et on informe l'utilisateur le cas échéant.
        if krgv['id'] is None:
            flash(_('No event has been selected'), 'warning')
            raise redirect(request.environ.get('HTTP_REFERER', url('/')))
        ids = krgv['id'].split(',')
        
        # Si des changements sont survenus depuis que la 
        # page est affichée, on en informe l'utilisateur.
        if datetime.fromtimestamp(float(krgv['last_modification'])) \
                                        < get_last_modification_timestamp(ids):
            flash(_('Changes have occurred since the page was displayed, '
                    'please refresh it.'), 'warning')
            print "\n\n\n\n ##### ", datetime.fromtimestamp(float(krgv['last_modification'])), " #####"
            print "##### ", get_last_modification_timestamp(ids), "\n\n\n\n"
            raise redirect(request.environ.get('HTTP_REFERER', url('/')))

        # Si l'utilisateur édite plusieurs événements à la fois,
        # il nous faut chacun des identifiants
       
        if len(ids) > 1 :
            ids = ids[:-1]
        
        username = request.environ['repoze.who.identity']['repoze.who.userid']
        events = VigiboardRequest(User.by_user_name(username))
        events.add_filter(CorrEvent.idcorrevent.in_(ids))
        
        # Vérification que au moins un des identifiants existe et est éditable
        if events.num_rows() <= 0 :
            flash(_('No access to this event'), 'error')
            redirect('/')
        
        # Modification des événements et création d'un historique
        # pour chacun d'eux.
        for req in events.req:
            if isinstance(req, CorrEvent):
                event = req
            else:
                event = req[0]

            if krgv['trouble_ticket'] != '' :
                history = EventHistory(
                        type_action="Ticket change",
                        idevent=event.idcause,
                        value=krgv['trouble_ticket'],
                        text=_("Changed trouble ticket from '%s' to '%s'") % (
                            event.trouble_ticket, krgv['trouble_ticket']
                        ),
                        username=username,
                        timestamp=datetime.now(),
                    )
                DBSession.add(history)   
                event.trouble_ticket = krgv['trouble_ticket']

            if krgv['ack'] != 'NoChange' :
                history = EventHistory(
                        type_action="Acknowlegement change state",
                        idevent=event.idcause,
                        value=krgv['ack'],
                        text=_("Changed acknowledgement status from '%s' to '%s'") % (
                            event.status, krgv['ack']
                        ),
                        username=username,
                        timestamp=datetime.now(),
                    )
                DBSession.add(history)
                event.status = krgv['ack']

        DBSession.flush()
        flash(_('Updated successfully'))
        redirect(request.environ.get('HTTP_REFERER', url('/')))


    @validate(validators={"plugin_name": validators.OneOf(
        [i for [i, j] in config.get('vigiboard_plugins', [])])},
                error_handler = process_form_errors)
    @expose('json')
    def get_plugin_value(self, plugin_name, *arg, **krgv):
        """
        Permet aux plugins de pouvoir récupérer des valeurs Json
        """
        plugins = config['vigiboard_plugins']
        if plugins is None:
            return

        plugin = [i for i in plugins if i[0] == plugin_name][0]
        try:
            mypac = __import__(
                'vigiboard.controllers.vigiboard_plugin.' + plugin[0],
                globals(), locals(), [plugin[1]], -1)
            plug = getattr(mypac, plugin[1])()
            return plug.controller(*arg, **krgv)
        except:
            raise
    
#    @validate(validators= {"fontsize": validators.Int()},
#                    error_handler = process_form_errors)
    @expose('json')
    def set_fontsize(self, fontsize):
        """
        Save font size
        """
        session['fontsize'] = fontsize
        session.save()
        return dict()

    @validate(validators={"refresh": validators.Int()},
            error_handler=process_form_errors)
    @expose('json')
    def set_refresh(self, refresh):
        """
        Save refresh time
        """
        session['refresh'] = refresh
        session.save()
        return dict()

    @expose('json')
    def set_theme(self, theme):
        """
        Save theme to use time
        """
        session['theme'] = theme
        session.save()
        return dict()
    
def get_last_modification_timestamp(event_id_list):
    """
    Récupère le timestamp de la dernière modification 
    opérée sur l'un des événements dont l'identifiant
    fait partie de la liste passée en paramètre.
    """
    last_modification_timestamp = DBSession.query(
                                func.max(EventHistory.timestamp),
                         ).filter(EventHistory.idevent.in_(event_id_list)
                         ).scalar()
                         
    if not last_modification_timestamp:
        last_modification_timestamp = datetime.now()
    # On élimine la fraction (microsecondes) de l'objet datetime.
    # XXX Dans l'idéal, on devrait gérer les microsecondes.
    # Problème: les erreurs d'arrondis empêchent certaines modifications.
    return datetime.fromtimestamp(mktime(
        last_modification_timestamp.timetuple()))

