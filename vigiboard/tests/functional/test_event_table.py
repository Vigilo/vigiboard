# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test du tableau d'événements de Vigiboard
"""

from nose.tools import assert_true, assert_equal
from datetime import datetime
import tg
import transaction

from vigiboard.model import DBSession, \
    Event, EventHistory, CorrEvent, \
    Permission, User, StateName, \
    Host, HostGroup, ServiceLowLevel, ServiceGroup
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboardrequest import VigiboardRequest
from vigiboard.controllers.vigiboard_plugin.tests import MonPlugin


class TestEventTable(TestController):
    """
    Test du tableau d'événements de Vigiboard
    """

def populate_DB():
    """ Peuple la base de données. """

    # On ajoute des noms d'états.
    DBSession.add(StateName(statename=u'OK', order=0))
    DBSession.add(StateName(statename=u'WARNING', order=2))
    DBSession.flush()
    transaction.commit()

    # On ajoute les groupes et leurs dépendances
    hosteditors = HostGroup(name=u'editorsgroup')
    DBSession.add(hosteditors)
    hostmanagers = HostGroup(name=u'managersgroup', parent=hosteditors)
    DBSession.add(hostmanagers)
    DBSession.flush()

    manage_perm = Permission.by_permission_name(u'manage')
    edit_perm = Permission.by_permission_name(u'edit')

    hostmanagers.permissions.append(manage_perm)
    hosteditors.permissions.append(edit_perm)
    DBSession.flush()

    # Création des hôtes de test.
    host_template = {
        'checkhostcmd': u'halt',
        'snmpcommunity': u'public',
        'hosttpl': u'/dev/null',
        'mainip': u'192.168.1.1',
        'snmpport': 42,
        'weight': 42,
    }

    managerhost = Host(name=u'managerhost', **host_template)
    editorhost = Host(name=u'editorhost', **host_template)
    DBSession.add(managerhost)
    DBSession.add(editorhost)

    # Affectation des hôtes aux groupes.
    hosteditors.hosts.append(editorhost)
    hostmanagers.hosts.append(managerhost)
    DBSession.flush()

    # Ajout des événements eux-mêmes
    event_template = {
        'message': u'foo',
        'current_state': StateName.statename_to_value(u'WARNING'),
    }

    event1 = Event(supitem=service1, **event_template)
    event2 = Event(supitem=service2, **event_template)
    event3 = Event(supitem=service3, **event_template)
    event4 = Event(supitem=service4, **event_template)
    event5 = Event(supitem=editorhost, **event_template)
    event6 = Event(supitem=managerhost, **event_template)

    DBSession.add(event1)
    DBSession.add(event2)
    DBSession.add(event3)
    DBSession.add(event4)
    DBSession.add(event5)
    DBSession.add(event6)
    DBSession.flush()

    # Ajout des événements corrélés
    aggregate_template = {
        'timestamp_active': datetime.now(),
        'priority': 1,
        'status': u'None',
    }
    aggregate1 = CorrEvent(
        idcause=event1.idevent, **aggregate_template)
    aggregate2 = CorrEvent(
        idcause=event4.idevent, **aggregate_template)
    aggregate3 = CorrEvent(
        idcause=event5.idevent, **aggregate_template)
    aggregate4 = CorrEvent(
        idcause=event6.idevent, **aggregate_template)

    aggregate1.events.append(event1)
    aggregate1.events.append(event3)
    aggregate2.events.append(event4)
    aggregate2.events.append(event2)
    aggregate3.events.append(event5)
    aggregate4.events.append(event6)
    DBSession.add(aggregate1)
    DBSession.add(aggregate2)
    DBSession.add(aggregate3)
    DBSession.add(aggregate4)
    DBSession.flush()
    transaction.commit()

    def test_event_table(self):
        """
        Test du tableau d'évènements de la page d'accueil de Vigiboard.
        """

        populate_DB()

        ### 1er cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'editor'.
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)

        # Il doit y avoir 2 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 2)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

        ### 2nd cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'manager'.
        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)

        # Il doit y avoir 4 lignes de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 4)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)



