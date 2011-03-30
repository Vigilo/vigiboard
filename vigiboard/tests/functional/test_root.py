# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import assert_true, assert_false, assert_equal
from nose import SkipTest
from datetime import datetime
from time import mktime
import transaction

from vigilo.models.session import DBSession
from vigilo.models.tables import Event, EventHistory, CorrEvent, User, \
                            Permission, StateName, Host, UserGroup, \
                            SupItemGroup, LowLevelService, DataPermission
from vigiboard.tests import TestController
from tg import config

def populate_DB():
    """ Peuple la base de données. """
    # On ajoute un groupe d'hôtes et un groupe de services.
    supitemmanagers = SupItemGroup(name = u'managersgroup', parent=None)
    DBSession.add(supitemmanagers)
    DBSession.flush()

    usergroup = UserGroup.by_group_name(u'users_with_access')
    DBSession.add(DataPermission(
        group=supitemmanagers,
        usergroup=usergroup,
        access=u'w',
    ))
    DBSession.flush()

    # On crée un 2 hôtes, et on les ajoute au groupe d'hôtes.
    host1 = Host(
        name = u'host1',
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        address = u'192.168.1.1',
        snmpport = 42,
        weight = 42,
    )
    DBSession.add(host1)
    supitemmanagers.supitems.append(host1)
    host2 = Host(
        name = u'host2',
        checkhostcmd = u'halt',
        snmpcommunity = u'public',
        hosttpl = u'/dev/null',
        address = u'192.168.1.1',
        snmpport = 42,
        weight = 42,
    )
    DBSession.add(host2)
    supitemmanagers.supitems.append(host2)
    DBSession.flush()

    # On crée 2 services de bas niveau, et on les ajoute au groupe de services.
    service1 = LowLevelService(
        host = host1,
        servicename = u'service1',
        command = u'halt',
        weight = 42,
    )
    DBSession.add(service1)
    supitemmanagers.supitems.append(service1)
    service2 = LowLevelService(
        host = host2,
        servicename = u'service2',
        command = u'halt',
        weight = 42,
    )
    DBSession.add(service2)
    supitemmanagers.supitems.append(service2)
    DBSession.flush()

    return ([host1, host2], [service1, service2])

def add_correvent_caused_by(supitem, timestamp,
        correvent_status=u"None", event_status=u"WARNING"):
    """
    Ajoute dans la base de données un évènement corrélé causé
    par un incident survenu sur l'item passé en paramètre.
    Génère un historique pour les tests.
    """

    # Ajout d'un événement
    event = Event(
        supitem = supitem,
        message = u'foo',
        current_state = StateName.statename_to_value(event_status),
        timestamp = datetime.now(),
    )
    DBSession.add(event)
    DBSession.flush()

    # Ajout d'un événement corrélé
    aggregate = CorrEvent(
        idcause = event.idevent,
        timestamp_active = timestamp,
        priority = 1,
        status = correvent_status)
    aggregate.events.append(event)
    DBSession.add(aggregate)
    DBSession.flush()

    return aggregate.idcorrevent


class TestRootController(TestController):
    """ Classe de test du root controller """
    def setUp(self):
        super(TestRootController, self).setUp()
        perm = Permission.by_permission_name(u'vigiboard-access')
        perm2 = Permission.by_permission_name(u'vigiboard-update')

        user = User(
            user_name=u'access',
            fullname=u'',
            email=u'user.has@access',
        )
        usergroup = UserGroup(group_name=u'users_with_access')
        usergroup.permissions.append(perm)
        usergroup.permissions.append(perm2)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

        user = User(
            user_name=u'limited_access',
            fullname=u'',
            email=u'user.has.no@access',
        )
        usergroup = UserGroup(group_name=u'users_with_limited_access')
        usergroup.permissions.append(perm)
        usergroup.permissions.append(perm2)
        user.usergroups.append(usergroup)
        DBSession.add(user)
        DBSession.add(usergroup)
        DBSession.flush()

    def test_index(self):
        """Test that access to the root webpage is restricted."""

        response = self.app.get('/', status=401)
        msg = 'Unauthorized'
        assert_true(msg in response)

    def test_update_host_correvents_status(self):
        """Màj du statut d'évènements corrélés causés par des hôtes"""

        # On peuple la BDD avec 2 hôtes, 2 services de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (hosts, services) = populate_DB()

        # On ajoute 2 évènements corrélés causés par ces hôtes
        timestamp = datetime.now()
        correvent1_id = add_correvent_caused_by(hosts[0], timestamp)
        correvent2_id = add_correvent_caused_by(hosts[1], timestamp)
        transaction.commit()

        ### 1er cas : L'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : u"foo",
                "ack" : u'NoChange',
            }, status = 401)

        ### 2ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'limited_access'.
        environ = {'REMOTE_USER': 'limited_access'}

        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas la permission de modifier ces évènements.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "ack" : u'NoChange',
                "trouble_ticket" : u"foo",
                "last_modification": mktime(timestamp.timetuple()),
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 3ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'access'.
        environ = {'REMOTE_USER': 'access'}

        # On s'attend à ce que le statut de la requête soit 302,
        # et à ce qu'un message informe l'utilisateur que les
        # évènements corrélés sélectionnées ont bien été mis à jour.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : u"foo",
                "ack" : u'NoChange',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_false(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="ok"]'))

        # On s'assure que le ticket de l'évènement corrélé
        # a bien été mis à jour dans la base de données.
        correvents = DBSession.query(
            CorrEvent.trouble_ticket
            ).filter(CorrEvent.idcorrevent.in_([correvent1_id, correvent2_id])
            ).all()

        assert_equal(correvents[0].trouble_ticket, u"foo")
        assert_equal(correvents[1].trouble_ticket, u"foo")

    def test_update_service_correvents_status(self):
        """Màj du statut d'évènements corrélés causés par des SBN"""

        # On peuple la BDD avec 2 hôtes, 2 services de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (hosts, services) = populate_DB()

        # On ajoute 2 évènements corrélés causés par ces hôtes
        timestamp = datetime.now()
        correvent1_id = add_correvent_caused_by(services[0], timestamp)
        correvent2_id = add_correvent_caused_by(services[1], timestamp)

        transaction.commit()

        ### 1er cas : L'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : u"foo",
                "ack" : u'NoChange',
            }, status = 401)

        ### 2ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'limited_access'.
        environ = {'REMOTE_USER': 'limited_access'}

        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas la permission de modifier ces évènements.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : u"foo",
                "ack" : u'NoChange',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 3ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'access'.
        environ = {'REMOTE_USER': 'access'}

        # On s'attend à ce que le statut de la requête soit 302,
        # et à ce qu'un message informe l'utilisateur que les
        # évènements corrélés sélectionnées ont bien été mis à jour.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : u"foo",
                "ack" : u'NoChange',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_false(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="ok"]'))

        # On s'assure que le ticket de l'évènement corrélé
        # a bien été mis à jour dans la base de données.
        correvents = DBSession.query(
            CorrEvent.trouble_ticket
            ).filter(CorrEvent.idcorrevent.in_([correvent1_id, correvent2_id])
            ).all()
        assert_equal(correvents[0].trouble_ticket, u"foo")
        assert_equal(correvents[1].trouble_ticket, u"foo")

    def test_update_host_correvents_tickets(self):
        """Màj de tickets d'évènements corrélés causés par des hôtes"""

        # On peuple la BDD avec 2 hôtes, 2 services de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (hosts, services) = populate_DB()

        # On ajoute 2 évènements corrélés causés par ces hôtes
        timestamp = datetime.now()
        correvent1_id = add_correvent_caused_by(hosts[0], timestamp)
        correvent2_id = add_correvent_caused_by(hosts[1], timestamp)
        transaction.commit()

        ### 1er cas : L'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 401)

        ### 2ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'limited_access'.
        environ = {'REMOTE_USER': 'limited_access'}

        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas la permission de modifier ces évènements.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 3ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'access'.
        environ = {'REMOTE_USER': 'access'}

        # On s'attend à ce que le statut de la requête soit 302,
        # et à ce qu'un message informe l'utilisateur que les
        # évènements corrélés sélectionnées ont bien été mis à jour.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_false(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="ok"]'))

        # On s'assure que le statut de l'évènement corrélé
        # a bien été mis à jour dans la base de données.
        correvents = DBSession.query(
            CorrEvent.status
            ).filter(CorrEvent.idcorrevent.in_([correvent1_id, correvent2_id])
            ).all()
        assert_equal(correvents[0].status, u'Acknowledged')
        assert_equal(correvents[1].status, u'Acknowledged')


    def test_update_service_correvents_tickets(self):
        """Màj de tickets d'évènements corrélés causés par des SBN"""

        # On peuple la BDD avec 2 hôtes, 2 services de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (hosts, services) = populate_DB()

        # On ajoute 2 évènements corrélés causés par ces hôtes
        timestamp = datetime.now()
        correvent1_id = add_correvent_caused_by(services[0], timestamp)
        correvent2_id = add_correvent_caused_by(services[1], timestamp)

        transaction.commit()

        ### 1er cas : L'utilisateur n'est pas connecté.
        # On vérifie que le plugin retourne bien une erreur 401.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 401)

        ### 2ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'limited_access'.
        environ = {'REMOTE_USER': 'limited_access'}

        # On s'attend à ce qu'une erreur 302 soit renvoyée, et à
        # ce qu'un message d'erreur précise à l'utilisateur qu'il
        # n'a pas la permission de modifier ces évènements.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))

        ### 3ème cas : L'utilisateur utilisé pour
        # se connecter à Vigiboard est 'access'.
        environ = {'REMOTE_USER': 'access'}

        # On s'attend à ce que le statut de la requête soit 302,
        # et à ce qu'un message informe l'utilisateur que les
        # évènements corrélés sélectionnées ont bien été mis à jour.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id) + "," + str(correvent2_id),
                "last_modification": mktime(timestamp.timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_false(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="ok"]'))

        # On s'assure que le statut de l'évènement corrélé
        # a bien été mis à jour dans la base de données.
        correvents = DBSession.query(
            CorrEvent.status
            ).filter(CorrEvent.idcorrevent.in_([correvent1_id, correvent2_id])
            ).all()
        assert_equal(correvents[0].status, u'Acknowledged')
        assert_equal(correvents[1].status, u'Acknowledged')

    def test_update_while_data_have_changed(self):
        """Màj d'un évènement corrélé modifié entre temps."""

        # On peuple la BDD avec 2 hôtes, 2 services de bas niveau,
        # et un groupe d'hôtes et de services associés à ces items.
        (hosts, services) = populate_DB()

        # On ajoute 2 évènements corrélés causés par ces hôtes
        timestamp = datetime.now()
        correvent1_id = add_correvent_caused_by(services[0], timestamp)
        correvent2_id = add_correvent_caused_by(services[1], timestamp)

        # Date de modification du premier évènement corrélé
        later_date = datetime.now()
        # Date du chargement de la page
        date = mktime(later_date.timetuple()) - 42

        # On ajoute une entrée dans l'historique de l'évènement brut
        # causant le premier évènement corrélé, portant pour timestamp
        # une date postérieure à celle du chargement de la page.
        correvent1 = DBSession.query(
            CorrEvent.idcause
            ).filter(CorrEvent.idcorrevent == correvent1_id).one()
        DBSession.add(EventHistory(
            type_action = u'Nagios update state',
            idevent = correvent1.idcause,
            timestamp = later_date))
        DBSession.flush()

        transaction.commit()

        # L'utilisateur utilisé pour se connecter à Vigiboard est 'access'.
        environ = {'REMOTE_USER': 'access'}

        # On s'attend à ce que le statut de la requête soit 302, et
        # à ce qu'un message d'erreur avise l'utilisateur que des
        # changements sont intervenus depuis le chargement de la page.
        response = self.app.post(
            '/update', {
                "id" : str(correvent1_id),
                "last_modification" : date,
                "trouble_ticket" : "",
                "ack" : u'Acknowledged',
            }, status = 302, extra_environ = environ)

        response = response.follow(status=200, extra_environ = environ)
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="warning"]'))

        # On s'assure que le statut de l'évènement corrélé
        # n'a pas été modifié dans la base de données.
        status = DBSession.query(
            CorrEvent.status
            ).filter(CorrEvent.idcorrevent == correvent1_id
            ).scalar()
        assert_equal(status, u'None')

    def test_close_last_page(self):
        """
        Suppression de tous les événements de la dernière page.

        Lorsqu'on supprime tous les événements de la page, on doit
        implicitement afficher le contenu de la page d'avant.
        """
        raise SkipTest("Not ready yet")

        # On crée autant d'événements qu'on peut en afficher par page + 1,
        # afin d'avoir 2 pages dans le bac à événements.
        items_per_page = int(config['vigiboard_items_per_page'])
        for i in xrange(items_per_page + 1):
            host = Host(
                name = u'host%d' % i,
                checkhostcmd = u'halt',
                snmpcommunity = u'public',
                hosttpl = u'/dev/null',
                address = u'192.168.1.%d' % i,
                snmpport = 42,
                weight = 42,
            )
            DBSession.add(host)
            DBSession.flush()
            add_correvent_caused_by(host, datetime.now())
#        transaction.commit()

        environ = {'REMOTE_USER': 'manager'}

        # On vérifie qu'on a 2 pages et que sur la 2ème page,
        # il n'y a qu'un seul événement.
        response = self.app.get('/?page=2', extra_environ=environ)

        print [(e.idcorrevent, e.idcause) for e in DBSession.query(CorrEvent).all()]
        raise ValueError, str(response.body).decode('ascii', 'ignore')

        current_page = response.lxml.xpath(
            '//span[@class="pager_curpage"]/text()')
        assert_equal(2, int(current_page[0]))
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        assert_equal(len(rows), 1)

        # On force l'état de l'événement sur la 2ème page à 'OK'.
        # - Tout d'abord, on récupère l'identifiant de l'événement en question.
        idcorrevent = response.lxml.xpath('string(//table[@class="vigitable"]/tbody/tr/td[@class="plugin_details"]/a/@href)')
        idcorrevent = int(idcorrevent.lstrip('#'))
        # - Puis, on met à jour son état (en le forçant à OK).
        # On s'attend à ce que le statut de la requête soit 302,
        # et à ce qu'un message informe l'utilisateur que les
        # évènements corrélés sélectionnées ont bien été mis à jour.
        response = self.app.post(
            '/update', {
                "id" : str(idcorrevent),
                "last_modification": mktime(datetime.now().timetuple()),
                "trouble_ticket" : "",
                "ack" : u'Forced',
            }, status=302, extra_environ=environ)
        # - On s'assure que la mise à jour a fonctionné.
        response = response.follow(status=200, extra_environ=environ)
        assert_false(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="error"]'))
        assert_true(response.lxml.xpath(
            '//div[@id="flash"]/div[@class="ok"]'))

        # Une requête sur la 2ème page doit désormais afficher
        # le contenu de la 1ère page, et le nombre d'événements
        # doit être le même qu'au départ - 1.
        response = self.app.get('/?page=2', extra_environ=environ)
        current_page = response.lxml.xpath(
            '//span[@class="pager_curpage"]/text()')
        assert_equal(1, int(current_page[0]))
        rows = response.lxml.xpath('//table[@class="vigitable"]/tbody/tr')
        assert_equal(len(rows), items_per_page)
