# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""
Test de la classe User Utils
"""
from nose.tools import assert_true

from vigiboard.model import DBSession, Groups, Permission, \
        GroupPermissions
from vigiboard.tests import TestController
from vigiboard.controllers.vigiboard_ctl import get_user_groups
from vigiboard.tests import teardown_db
import tg
import transaction


class TestUserUtils(TestController):
    """Test de la classe User Utils"""
    
    def tearDown(self):
        """TearDown methode for Nose"""

        DBSession.rollback()
        teardown_db()
        transaction.begin() 

    def test_get_user_groups(self):
        """
        Manager est dans le group hostmanagers et hosteditors
        et Editor seulement dans hosteditors
        """
        
        # On commence par peupler la base
        
        DBSession.add(Groups(name = "hostmanagers"))
        DBSession.add(Groups(name = "hosteditors", parent="hostmanagers"))
        DBSession.query(Permission).filter(
            Permission.permission_name == u'manage')[0].permission_id
        idmanagers = DBSession.query(Permission).filter(
                Permission.permission_name == u'manage')[0].permission_id
        ideditors = DBSession.query(Permission
                ).filter(Permission.permission_name == u'edit')[0].permission_id
        DBSession.add(GroupPermissions(groupname = "hostmanagers",
                idpermission = idmanagers))
        DBSession.add(GroupPermissions(groupname = "hosteditors",
                idpermission = ideditors))

        # On commit car app.get fait un rollback ou équivalent
        
        transaction.commit()        
        
        # On obtient les variables de sessions comme si on était loggué
        # en tant que manager

        environ = {'REMOTE_USER': 'manager'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request
        
        # On récupère la liste des groups auquel on appartient
        
        grp = get_user_groups()

        # On vérifi que la liste est correcte (vérifi la gestion des
        # groupes sous forme d'arbre)
        
        assert_true( 'hostmanagers' in grp and 'hosteditors' in grp ,
            msg = "il est dans %s" % grp)
        
        # On recommence pour l'utilisateur editor
        
        environ = {'REMOTE_USER': 'editor'}
        response = self.app.get('/', extra_environ=environ)
        tg.request = response.request
        
        grp = get_user_groups()
        
        assert_true( not('hostmanagers' in grp) and 'hosteditors' in grp,
            msg = "il est dans %s" % grp)