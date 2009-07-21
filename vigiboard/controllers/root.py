# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect, config

from pylons.i18n import ugettext as _, lazy_ugettext as l_
from catwalk.tg2 import Catwalk
from repoze.what import predicates

from vigiboard.lib.base import BaseController
from vigiboard.model import DBSession 
from vigiboard.controllers.error import ErrorController
from vigiboard import model
from vigiboard.controllers.secure import SecureController

__all__ = ['RootController']

class RootController(BaseController):
    """
    The root controller for the vigiboard application.
    
    All the other controllers and WSGI applications should be mounted on this
    controller. For example::
    
        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()
    
    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.
    
    """
    secc = SecureController()
    
    admin = Catwalk(model, DBSession)
    
    error = ErrorController()

    # on charge les controleurs souhaité en dynamique
    def __init__(self) :
        super(RootController,self).__init__()
        
        for mod in config['vigilo_mods']:
            try :
                mymod = __import__(
                    'vigiboard.controllers.' + mod + '_ctl',globals(), locals(), [mod + 'Controller'],-1)
                setattr(self,mod,getattr(mymod,mod + 'Controller')())
            except:
                pass

    @expose('vigiboard.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('vigiboard.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('vigiboard.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')

    @expose('vigiboard.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('vigiboard.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('vigiboard.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
