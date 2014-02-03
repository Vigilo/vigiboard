# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (C) 2007-2013 CS-SI
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
################################################################################

"""Setup the vigiboard application"""

# pylint: disable-msg=W0613
# W0613: Unused arguments: on doit respecter l'API

__all__ = ['setup_app', 'populate_db']

def _(msg):
    """
    Cette fonction n'est jamais exécutée.
    Elle permet simplement de forcer la traduction de
    chaînes provenant de vigilo-turbogears
    """
    _('Vigilo has detected a breakdown on the following '
      'collector(s): %(list)s')

def setup_app(command, conf, variables):
    """Place any commands to setup vigiboard here"""
    from vigilo.turbogears import populate_db as tg_pop_db
    from vigiboard.config.environment import load_environment

    load_environment(conf.global_conf, conf.local_conf)
    tg_pop_db()

def populate_db(bind):
    from vigilo.models.session import DBSession
    from vigilo.models import tables

    permissions = {
        'vigiboard-access':
            'Gives access to VigiBoard',

        'vigiboard-update':
            'Allows users to update events',

        'vigiboard-admin':
            'Allows users to forcefully close open events',

        'vigiboard-silence':
            'Allows users to view and edit silence rules',
    }

    for (permission_name, description) in permissions.iteritems():
        if not tables.Permission.by_permission_name(unicode(permission_name)):
            DBSession.add(tables.Permission(
                permission_name=unicode(permission_name),
                description=unicode(description),
            ))
    DBSession.flush()
