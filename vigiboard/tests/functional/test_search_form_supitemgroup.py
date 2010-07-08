# -*- coding: utf-8 -*-
"""
Teste le formulaire de recherche avec un groupe d'hôtes.
"""
from nose.tools import assert_true, assert_equal
from datetime import datetime
import transaction

from vigiboard.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import SupItemGroup, Host, Permission, StateName, \
                                    Event, CorrEvent, User, UserGroup, \
                                    DataPermission
from vigilo.models.tables.grouphierarchy import GroupHierarchy

def insert_deps():
    """Insère les dépendances nécessaires aux tests."""
    timestamp = datetime.now()

    supitemgroup = SupItemGroup(
        name=u'foo',
    )
    DBSession.add(supitemgroup)
    DBSession.flush()

    DBSession.add(GroupHierarchy(
        parent=supitemgroup,
        child=supitemgroup,
        hops=0,
    ))
    DBSession.flush()

    host = Host(
        name=u'bar',
        checkhostcmd=u'',
        description=u'',
        hosttpl=u'',
        address=u'127.0.0.1',
        snmpport=42,
        snmpcommunity=u'public',
        snmpversion=u'3',
        weight=42,
    )
    DBSession.add(host)
    DBSession.flush()

    supitemgroup.supitems.append(host)
    DBSession.flush()

    event = Event(
        supitem=host,
        timestamp=timestamp,
        current_state=StateName.statename_to_value(u'WARNING'),
        message=u'Hello world',
    )
    DBSession.add(event)
    DBSession.flush()

    correvent = CorrEvent(
        impact=42,
        priority=42,
        trouble_ticket=None,
        status=u'None',
        occurrence=42,
        timestamp_active=timestamp,
        cause=event,
    )
    correvent.events.append(event)
    DBSession.add(correvent)
    DBSession.flush()
    return supitemgroup

class TestSearchFormSupItemGroup(TestController):
    """Teste la récupération d'événements selon le supitemgroup."""
    def setUp(self):
        super(TestSearchFormSupItemGroup, self).setUp()
        perm = Permission.by_permission_name(u'vigiboard-access')
        user = User(
            user_name=u'user',
            fullname=u'',
            email=u'some.random@us.er',
        )
        usergroup = UserGroup(
            group_name=u'users',
        )
        user.usergroups.append(usergroup)
        usergroup.permissions.append(perm)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

    def test_search_supitemgroup_when_allowed(self):
        """Teste la recherche par supitemgroup avec les bons droits d'accès."""
        # On crée un groupe d'hôte appelé 'foo',
        # contenant un hôte 'bar', ainsi qu'un événement
        # et un événement corrélé sur cet hôte.
        # De plus, on donne l'autorisation aux utilisateurs
        # ayant la permission 'edit' de voir cette alerte.
        supitemgroup = insert_deps()
        idgroup = supitemgroup.idgroup
        usergroup = UserGroup.by_group_name(u'users')
        DBSession.add(DataPermission(
            group=supitemgroup,
            usergroup=usergroup,
            access=u'r',
        ))
        DBSession.flush()
        transaction.commit()

        # On envoie une requête avec recherche sur le groupe d'hôtes créé,
        # on s'attend à recevoir 1 résultat.
        response = self.app.get('/?supitemgroup=%d' % idgroup,
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir plusieurs colonnes dans la ligne de résultats.
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_true(len(cols) > 1)

    def test_search_inexistent_supitemgroup(self):
        """Teste la recherche par supitemgroup sur un groupe inexistant."""
        # On envoie une requête avec recherche sur un groupe d'hôtes
        # qui n'existe pas, on s'attend à n'obtenir aucun résultat.
        transaction.commit()
        response = self.app.get('/?supitemgroup=%d' % -42,
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)

    def test_search_supitemgroup_when_disallowed(self):
        """Teste la recherche par supitemgroup SANS les droits d'accès."""
        # On crée un groupe d'hôte appelé 'foo',
        # contenant un hôte 'bar', ainsi qu'un événement
        # et un événement corrélé sur cet hôte.
        # MAIS, on NE DONNE PAS l'autorisation aux utilisateurs
        # de voir cette alerte, donc elle ne doit jamais apparaître.
        supitemgroup = insert_deps()
        idgroup = supitemgroup.idgroup
        transaction.commit()

        # On envoie une requête avec recherche sur le groupe d'hôtes créé,
        # mais avec un utilisateur ne disposant pas des permissions adéquates.
        # On s'attend à n'obtenir aucun résultat.
        response = self.app.get('/?supitemgroup=%d' % idgroup,
            extra_environ={'REMOTE_USER': 'user'})

        # Il doit y avoir 1 seule ligne de résultats.
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        print "There are %d rows in the result set" % len(rows)
        assert_equal(len(rows), 1)

        # Il doit y avoir 1 seule colonne dans la ligne de résultats.
        # (la colonne contient le texte "Il n'y a aucun événément", traduit)
        cols = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr/td')
        print "There are %d columns in the result set" % len(cols)
        assert_equal(len(cols), 1)
