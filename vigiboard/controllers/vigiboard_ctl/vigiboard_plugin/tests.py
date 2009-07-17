# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 

from vigiboard.controllers.vigiboard_ctl.vigiboard_plugin import \
	        VigiboardRequestPlugin
from vigiboard.model import EventHistory, Events

class MonPlugin(VigiboardRequestPlugin):
    """Plugin de test"""
    
    def __init__(self):
        super(PluginSHN,self).__init__(
            table = [EventHistory.idevent],
            join = [(EventHistory, EventHistory.idevent == Events.idevent)]
        )

    def show(self, req):
	"""Fonction d'affichage"""
	return req[1]
